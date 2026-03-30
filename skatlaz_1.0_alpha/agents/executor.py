#agents/executor.py

from skatlaz_llms_prompt import (
    generate_code,
    generate_article,
    generate_game,
    generate_image
)

class ExecutorAgent:

    def run(self, plan):
        results = []

        steps = plan.split("\n") if plan else []

        for step in steps:
            step = step.strip()

            if not step:
                continue

            try:
                if "code" in step.lower():
                    res = generate_code(step)

                elif "image" in step.lower():
                    res = generate_image(step)

                else:
                    res = generate_text(step)

                results.append(res)

            except Exception:
                results.append(f"[FAILED STEP]: {step}")

        return "\n\n".join(results) if results else "No result generated."
