import { motion } from "motion/react";

export function Waiting({ stage, ingredients, steps }: { stage: string; ingredients: string[]; steps: number }) {
  const label = stage === "checking" ? "Checking the recipe" :
    stage === "fixing" ? "Making corrections" : stage === "done" ? "Saving the reply" : "Writing your recipe";
  return <section className="waiting card">
    <div className="waiting-dots" aria-hidden="true">
      {[0, 1, 2, 3, 4].map((dot) => <motion.span key={dot} animate={{ y: [0, -9, 0], opacity: [0.45, 1, 0.45] }}
        transition={{ duration: 1.25, delay: dot * 0.12, repeat: Infinity }} />)}
    </div>
    <h2 aria-live="polite">{label}</h2>
    <p className="subtle">You can leave this screen and reopen the recipe to check on it.</p>
    {(ingredients.length > 0 || steps > 0) && <div className="waiting-ingredients">
      {ingredients.slice(0, 12).map((name, index) => <motion.span className="chip" key={`${name}-${index}`}
        initial={{ opacity: 0, y: 7 }} animate={{ opacity: 1, y: 0 }}>{name}</motion.span>)}
      {steps > 0 && <span className="subtle">{steps} {steps === 1 ? "step" : "steps"}</span>}
    </div>}
  </section>;
}
