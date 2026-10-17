"""Builds business_agent.ipynb from the `# %% [section]` blocks in app.py, so both stay in sync."""
import re
from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parent.parent
sections = dict(re.findall(r"# %% \[(\w+)\]\n(.*?)(?=\n# %% \[|\Z)", (ROOT / "app.py").read_text(), re.S))

md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
cells = [
    md("# Cedar Path Tutoring: Agent-Powered Business Assistant\n"
       "**EECE 503P/798S: Agentic Systems, C3 Assignment**\n\n"
       "An agent for a fictional tutoring center in Beirut. It answers questions as **Lina**, the student "
       "advisor, routes each message (general question / lead collection / feedback), collects leads, logs "
       "feedback and unanswered questions through tool calls, reflects on its own draft before replying, "
       "and runs as a Gradio chatbot.\n\n"
       "```\nuser message -> router (LLM + keyword fallback) -> agent (persona + instructions + tools)\n"
       "             -> tool calls (record_customer_interest / record_feedback) -> reflection -> reply\n```"),
    md("## 0. Setup\nThe API key is read from `.env` (`OPENAI_API_KEY`, or `GEMINI_API_KEY` as an alternative). "
       "`.env` is git-ignored.\n\n"
       "**On Google Colab:** add `OPENAI_API_KEY` under Secrets (the key icon in the left sidebar) and turn on "
       "notebook access. The next cell installs the packages, loads the key, and asks you to upload "
       "`about_business.pdf` and `business_summary.txt` if the `me/` folder is missing. Locally it does nothing."),
    code('# Colab only: install packages, load the key from Colab Secrets, upload the business files.\n'
         'import os, sys\n'
         'if "google.colab" in sys.modules:\n'
         '    !pip -q install openai gradio pypdf python-dotenv\n'
         '    from google.colab import files, userdata\n'
         '    os.environ["OPENAI_API_KEY"] = "".join(userdata.get("OPENAI_API_KEY").split())  # drop stray spaces/newlines\n'
         '    os.makedirs("me", exist_ok=True)\n'
         '    for name in ["about_business.pdf", "business_summary.txt"]:\n'
         '        if not os.path.exists(f"me/{name}"):\n'
         '            print(f"Upload {name}")\n'
         '            for fname, data in files.upload().items():\n'
         '                open(f"me/{fname}", "wb").write(data)'),
    code(sections["setup"].strip()),
    md("## 1. Business identity\nThe business is described in `me/business_summary.txt` and `me/about_business.pdf`. "
       "Both are loaded and given to the agent as its only source of truth."),
    code(sections["knowledge"].strip()),
    md("## 2. Agent persona and instructions\nThe agent's identity is split into two clearly separate parts:\n"
       "- **Persona**: *who* the agent is. Shapes tone and style.\n"
       "- **Instructions**: *what* it must and must not do. Operational guardrails."),
    md("### 2a. PERSONA"),
    code(sections["persona"].strip()),
    md("### 2b. INSTRUCTIONS"),
    code(sections["instructions"].strip()),
    md("## 3. Tool functions\nTwo tools. Each one logs with a `print` **and** appends a line to a JSONL file in `logs/`."),
    code(sections["tools"].strip()),
    md("### Tool schemas (MCP style)\n"
       "| Tool | Parameters | Expected output |\n|---|---|---|\n"
       "| `record_customer_interest` | `email` (str, required), `name` (str, required), `message` (str, required) "
       "| `{status: \"recorded\" \\| \"error\", detail: str}` |\n"
       "| `record_feedback` | `question` (str, required) | `{status: \"recorded\", detail: str}` |\n\n"
       "Below, each tool is defined MCP-style (`name`, `description`, `inputSchema`, `outputSchema`) and then "
       "converted to the OpenAI function-calling format."),
    code(sections["tool_schemas"].strip()),
    md("Quick check that both tools work on their own:"),
    code('print(record_customer_interest("test.student@example.com", "Test Student", "Grade 10, physics"))\n'
         'print(record_feedback("Do you offer chess classes?"))\n'
         'print(record_customer_interest("not-an-email", "Bad Input", "should be rejected"))'),
    md("## 4. System prompt\nThe persona, instructions, business summary and PDF content are assembled into one `system_prompt`."),
    code(sections["system_prompt"].strip()),
    md("## 5. Router\nEvery message is classified into one of three intents **before** the agent acts:\n"
       "- `general_question` -> answer from the business information; log the question with `record_feedback` if it can't be answered\n"
       "- `lead_collection` -> push for name + email, then call `record_customer_interest`\n"
       "- `feedback` -> the first model call is **forced** to call `record_feedback`\n\n"
       "The router uses a small LLM classification call. If that call fails, keyword heuristics decide instead."),
    code(sections["router"].strip()),
    md("The router on sample messages, using both the LLM and the heuristic fallback:"),
    code('samples = [\n'
         '    "What are your opening hours on Saturday?",\n'
         '    "I want to sign my son up for SAT prep",\n'
         '    "sara.k@gmail.com",\n'
         '    "The tutor was 20 minutes late today, not happy.",\n'
         '    "Do you teach computer science?",\n'
         ']\n'
         'history = [{"role": "assistant", "content": "Could you share your name and email?"}]\n'
         'for s in samples:\n'
         '    print(f"{s!r:55} LLM: {route(s, history)[0]:18} heuristic: {heuristic_route(s)}")'),
    md("## 6. (Bonus) Reflection step\nBefore replying, a reviewer model checks the draft for six specific violations: "
       "invented facts, false \"I've recorded it\" claims, a name guessed from an email, a missing name/email "
       "request on the lead route, a skipped answer, and style (character, homework, length). It returns one "
       "true/false flag per rule. **The code** then decides whether to revise, and overrides the flags it can "
       "check itself: it knows which tools actually succeeded. The draft and the revised reply are printed and "
       "saved to `logs/reflections.jsonl`.\n\nThe reviewer uses `gpt-4.1-mini`. In testing, `gpt-4o-mini` "
       "over-revised correct replies and sometimes invented policies while \"fixing\" them."),
    code(sections["reflection"].strip()),
    md("## 7. Agent interaction\n`run_agent` gives the model the user input, chat history (short-term memory) and the tools. "
       "If the model calls a tool, the tool is run and its result goes back to the model. Otherwise the text is returned. "
       "Reflection runs last. If reflection finds an unanswered question that the model never logged, a safety net calls `record_feedback`."),
    code(sections["agent"].strip()),
    md("### Test conversation\nA short multi-turn chat that goes through every route. Watch for the `[ROUTER]`, `[TOOL]` and `[REFLECT]` lines."),
    code('history = []\n'
         'for user_msg in [\n'
         '    "Hi! How much is one-on-one tutoring for grade 11?",\n'
         '    "Is there parking near your center?",\n'
         '    "I\'d like to book the free assessment for my daughter, she\'s in grade 12",\n'
         '    "I\'m Rania Saleh, rania.saleh@example.com",\n'
         '    "Honestly the online session last week kept freezing, please fix your internet",\n'
         ']:\n'
         '    reply, trace = run_agent(user_msg, history)\n'
         '    print(f"USER: {user_msg}\\nLINA: {reply}\\n" + "=" * 80)\n'
         '    history += [{"role": "user", "content": user_msg}, {"role": "assistant", "content": reply}]'),
    md("Contents of the logs:"),
    code('for f in ["leads.jsonl", "feedback.jsonl", "reflections.jsonl"]:\n'
         '    path = LOG_DIR / f\n'
         '    print(f"--- {f} ---")\n'
         '    print(path.read_text() if path.exists() else "(empty)")'),
    md("## 8. Gradio interface\nA `ChatInterface` for the demo, with an **Agent trace** panel that shows the route, "
       "the tools called, and the reflection result for each message."),
    code(sections["gradio"].strip()),
]

nb = nbf.v4.new_notebook(cells=cells, metadata={
    "kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"},
    "language_info": {"name": "python"}})
nbf.write(nb, ROOT / "business_agent.ipynb")
print(f"Wrote business_agent.ipynb with {len(cells)} cells")
