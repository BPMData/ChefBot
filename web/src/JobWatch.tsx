import { useEffect, useState } from 'react';
import { RequestError, watchJob, type JobEvent } from './api';
import type { Pending } from './storage';

export type Terminal = Extract<JobEvent, { kind: 'result' | 'stopped' | 'error' }>;
export type JobView = {
  stage: string;
  ingredients: string[];
  steps: number;
  draft: string;
  paused?: string;
};
export const initialJobView: JobView = { stage: 'drafting', ingredients: [], steps: 0, draft: '' };

export function JobWatch({
  id,
  pending,
  retry,
  update,
  finish,
}: {
  id: string;
  pending: Pending;
  retry: object | null;
  update: (id: string, view: JobView | null) => void;
  finish: (id: string, pending: Pending, terminal?: Terminal) => Promise<void>;
}) {
  const [resume, setResume] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    const { signal } = controller;
    let timer: ReturnType<typeof setTimeout> | undefined;
    let paused = false;
    let view = initialJobView;
    function pause(message: string) {
      paused = true;
      update(pending.id, { ...view, paused: message });
    }
    const reconnect = () => {
      if (paused && document.visibilityState === 'visible') setResume((current) => current + 1);
    };
    window.addEventListener('online', reconnect);
    window.addEventListener('focus', reconnect);
    document.addEventListener('visibilitychange', reconnect);

    async function watch() {
      let terminal: Terminal | undefined;
      const event = (message: JobEvent) => {
        switch (message.kind) {
          case 'stage':
            view = { ...view, stage: message.stage };
            break;
          case 'progress':
            view = { ...view, ingredients: message.ingredients, steps: message.step_count };
            break;
          case 'draft':
            view = { ...view, draft: view.draft + message.delta };
            break;
          default:
            terminal = message;
            return;
        }
        update(pending.id, view);
      };

      for (let attempt = 0; !signal.aborted; attempt += 1) {
        view = initialJobView;
        update(pending.id, view);
        try {
          await watchJob(pending.id, event, signal);
          break;
        } catch (error) {
          if (signal.aborted) return;
          const missing = error instanceof RequestError && error.status === 404;
          const awaitingStart = pending.submittedAt !== undefined && Date.now() - pending.submittedAt < 20_000;
          const delays = missing && awaitingStart ? [800, 1600, 3200, 6400, 8000] : [800, 1600];
          if (missing && !awaitingStart) break;
          if (attempt >= delays.length) {
            if (missing) break;
            pause('The connection paused. Reconnect to check your recipe.');
            return;
          }
          await new Promise<void>((resolve) => {
            timer = setTimeout(resolve, delays[attempt]);
            signal.addEventListener(
              'abort',
              () => {
                clearTimeout(timer);
                resolve();
              },
              { once: true }
            );
          });
        }
      }
      if (signal.aborted) return;
      try {
        await finish(id, pending, terminal);
      } catch {
        if (!signal.aborted) pause('The recipe couldn’t be saved. Reconnect to try again.');
      }
    }
    void watch();
    return () => {
      controller.abort();
      window.removeEventListener('online', reconnect);
      window.removeEventListener('focus', reconnect);
      document.removeEventListener('visibilitychange', reconnect);
      update(pending.id, null);
    };
  }, [id, pending.id, pending.submittedAt, retry, resume, update, finish]);
  return null;
}
