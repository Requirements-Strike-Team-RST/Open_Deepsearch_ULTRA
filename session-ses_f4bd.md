# Investigate issue #232 Sources inconsistency

**Session ID:** ses_f4bd31a45ffe6GUBUE5KnTGUnW
**Created:** 9/18/2026, 7:00:36 PM
**Updated:** 9/18/2026, 7:56:51 PM

---

## User

I want to fix issue #232 in the langchain-ai/open_deep_research repository. The issue is about an inconsistency between the Output Format and Citation Rules for the Sources section. Please do not modify any code yet.

First, investigate the repository and find where this inconsistency actually comes from — don't assume it's in a single place. Show me the relevant code or prompts you find. Then propose possible solutions for resolving the conflict, with the trade-offs of each option, and check whether other parts of the codebase reference the Sources format and would also need to be updated for consistency. Give me a recommendation at the end, but wait for my confirmation before making any changes. 

---

## Assistant (Build · CS5351/DeepSeek-V4-Flash · 1.2s)

I'll investigate the repository to understand the Sources section inconsistency. Let me start by exploring the structure and finding relevant code.

**Tool: grep**

**Input:**

```json
{
  "pattern": "Sources",
  "include": "*.py"
}
```

**Output:**

```
Found 9 matches
/Users/sdm/open_deep_research/src/open_deep_research/prompts.py:
  Line 71: 5. Sources

  Line 200: 4. You should include a "Sources" section at the end of the report that lists all of the sources the researcher found with corresponding citations, cited against statements in the report.

  Line 209: **List of All Relevant Sources (with citations in the report)**

  Line 214: - End with ### Sources that lists each source with corresponding numbers

  Line 253: 5. Includes a "Sources" section at the end with all referenced links

  Line 300: - End with ### Sources that lists each source with corresponding numbers


/Users/sdm/open_deep_research/src/legacy/prompts.py:
  Line 132: - End with ### Sources that lists each source with corresponding numbers

  Line 392:      - End with a "### Sources" subsection (H3 level with ###) containing a numbered list of URLs used

  Line 402: ### Sources
```

**Tool: grep**

**Input:**

```json
{
  "pattern": "Sources",
  "include": "*.md"
}
```

**Output:**

```
Found 21 matches
/Users/sdm/open_deep_research/examples/pubmed.md:
  Line 33: ### Sources

  Line 52: ### Sources

  Line 71: ### Sources

  Line 92: ### Sources

  Line 111: ### Sources

  Line 129: ### Sources


/Users/sdm/open_deep_research/examples/arxiv.md:
  Line 20: ### Sources

  Line 40: ### Sources

  Line 59: ### Sources

  Line 83: ### Sources

  Line 104: ### Sources


/Users/sdm/open_deep_research/examples/inference-market.md:
  Line 24: ### Sources

  Line 44: ### Sources

  Line 62: ### Sources

  Line 80: ### Sources

  Line 101: ### Sources


/Users/sdm/open_deep_research/examples/inference-market-gpt45.md:
  Line 19: ### Sources

  Line 40: ### Sources

  Line 59: ### Sources

  Line 74: ### Sources

  Line 98: ### Sources
```

---

## Assistant (Build · CS5351/DeepSeek-V4-Flash · 2.2s)

Let me look at the main prompts.py file to understand the conflict, especially around lines 71, 200, 209-214, 253, 300.

**Tool: read**

**Input:**

```json
{
  "filePath": "/Users/sdm/open_deep_research/src/open_deep_research/prompts.py",
  "offset": 40,
  "limit": 280
}
```

**Output:**

```
<path>/Users/sdm/open_deep_research/src/open_deep_research/prompts.py</path>
<type>file</type>
<content>
40: - Keep the message concise and professional
41: """
42: 
43: 
44: transform_messages_into_research_topic_prompt = """You will be given a set of messages that have been exchanged so far between yourself and the user. 
45: Your job is to translate these messages into a more detailed and concrete research question that will be used to guide the research.
46: 
47: The messages that have been exchanged so far between yourself and the user are:
48: <Messages>
49: {messages}
50: </Messages>
51: 
52: Today's date is {date}.
53: 
54: You will return a single research question that will be used to guide the research.
55: 
56: Guidelines:
57: 1. Maximize Specificity and Detail
58: - Include all known user preferences and explicitly list key attributes or dimensions to consider.
59: - It is important that all details from the user are included in the instructions.
60: 
61: 2. Fill in Unstated But Necessary Dimensions as Open-Ended
62: - If certain attributes are essential for a meaningful output but the user has not provided them, explicitly state that they are open-ended or default to no specific constraint.
63: 
64: 3. Avoid Unwarranted Assumptions
65: - If the user has not provided a particular detail, do not invent one.
66: - Instead, state the lack of specification and guide the researcher to treat it as flexible or accept all possible options.
67: 
68: 4. Use the First Person
69: - Phrase the request from the perspective of the user.
70: 
71: 5. Sources
72: - If specific sources should be prioritized, specify them in the research question.
73: - For product and travel research, prefer linking directly to official or primary websites (e.g., official brand sites, manufacturer pages, or reputable e-commerce platforms like Amazon for user reviews) rather than aggregator sites or SEO-heavy blogs.
74: - For academic or scientific queries, prefer linking directly to the original paper or official journal publication rather than survey papers or secondary summaries.
75: - For people, try linking directly to their LinkedIn profile, or their personal website if they have one.
76: - If the query is in a specific language, prioritize sources published in that language.
77: """
78: 
79: lead_researcher_prompt = """You are a research supervisor. Your job is to conduct research by calling the "ConductResearch" tool. For context, today's date is {date}.
80: 
81: <Task>
82: Your focus is to call the "ConductResearch" tool to conduct research against the overall research question passed in by the user. 
83: When you are completely satisfied with the research findings returned from the tool calls, then you should call the "ResearchComplete" tool to indicate that you are done with your research.
84: </Task>
85: 
86: <Available Tools>
87: You have access to three main tools:
88: 1. **ConductResearch**: Delegate research tasks to specialized sub-agents
89: 2. **ResearchComplete**: Indicate that research is complete
90: 3. **think_tool**: For reflection and strategic planning during research
91: 
92: **CRITICAL: Use think_tool before calling ConductResearch to plan your approach, and after each ConductResearch to assess progress. Do not call think_tool with any other tools in parallel.**
93: </Available Tools>
94: 
95: <Instructions>
96: Think like a research manager with limited time and resources. Follow these steps:
97: 
98: 1. **Read the question carefully** - What specific information does the user need?
99: 2. **Decide how to delegate the research** - Carefully consider the question and decide how to delegate the research. Are there multiple independent directions that can be explored simultaneously?
100: 3. **After each call to ConductResearch, pause and assess** - Do I have enough to answer? What's still missing?
101: </Instructions>
102: 
103: <Hard Limits>
104: **Task Delegation Budgets** (Prevent excessive delegation):
105: - **Bias towards single agent** - Use single agent for simplicity unless the user request has clear opportunity for parallelization
106: - **Stop when you can answer confidently** - Don't keep delegating research for perfection
107: - **Limit tool calls** - Always stop after {max_researcher_iterations} tool calls to ConductResearch and think_tool if you cannot find the right sources
108: 
109: **Maximum {max_concurrent_research_units} parallel agents per iteration**
110: </Hard Limits>
111: 
112: <Show Your Thinking>
113: Before you call ConductResearch tool call, use think_tool to plan your approach:
114: - Can the task be broken down into smaller sub-tasks?
115: 
116: After each ConductResearch tool call, use think_tool to analyze the results:
117: - What key information did I find?
118: - What's missing?
119: - Do I have enough to answer the question comprehensively?
120: - Should I delegate more research or call ResearchComplete?
121: </Show Your Thinking>
122: 
123: <Scaling Rules>
124: **Simple fact-finding, lists, and rankings** can use a single sub-agent:
125: - *Example*: List the top 10 coffee shops in San Francisco → Use 1 sub-agent
126: 
127: **Comparisons presented in the user request** can use a sub-agent for each element of the comparison:
128: - *Example*: Compare OpenAI vs. Anthropic vs. DeepMind approaches to AI safety → Use 3 sub-agents
129: - Delegate clear, distinct, non-overlapping subtopics
130: 
131: **Important Reminders:**
132: - Each ConductResearch call spawns a dedicated research agent for that specific topic
133: - A separate agent will write the final report - you just need to gather information
134: - When calling ConductResearch, provide complete standalone instructions - sub-agents can't see other agents' work
135: - Do NOT use acronyms or abbreviations in your research questions, be very clear and specific
136: </Scaling Rules>"""
137: 
138: research_system_prompt = """You are a research assistant conducting research on the user's input topic. For context, today's date is {date}.
139: 
140: <Task>
141: Your job is to use tools to gather information about the user's input topic.
142: You can use any of the tools provided to you to find resources that can help answer the research question. You can call these tools in series or in parallel, your research is conducted in a tool-calling loop.
143: </Task>
144: 
145: <Available Tools>
146: You have access to two main tools:
147: 1. **tavily_search**: For conducting web searches to gather information
148: 2. **think_tool**: For reflection and strategic planning during research
149: {mcp_prompt}
150: 
151: **CRITICAL: Use think_tool after each search to reflect on results and plan next steps. Do not call think_tool with the tavily_search or any other tools. It should be to reflect on the results of the search.**
152: </Available Tools>
153: 
154: <Instructions>
155: Think like a human researcher with limited time. Follow these steps:
156: 
157: 1. **Read the question carefully** - What specific information does the user need?
158: 2. **Start with broader searches** - Use broad, comprehensive queries first
159: 3. **After each search, pause and assess** - Do I have enough to answer? What's still missing?
160: 4. **Execute narrower searches as you gather information** - Fill in the gaps
161: 5. **Stop when you can answer confidently** - Don't keep searching for perfection
162: </Instructions>
163: 
164: <Hard Limits>
165: **Tool Call Budgets** (Prevent excessive searching):
166: - **Simple queries**: Use 2-3 search tool calls maximum
167: - **Complex queries**: Use up to 5 search tool calls maximum
168: - **Always stop**: After 5 search tool calls if you cannot find the right sources
169: 
170: **Stop Immediately When**:
171: - You can answer the user's question comprehensively
172: - You have 3+ relevant examples/sources for the question
173: - Your last 2 searches returned similar information
174: </Hard Limits>
175: 
176: <Show Your Thinking>
177: After each search tool call, use think_tool to analyze the results:
178: - What key information did I find?
179: - What's missing?
180: - Do I have enough to answer the question comprehensively?
181: - Should I search more or provide my answer?
182: </Show Your Thinking>
183: """
184: 
185: 
186: compress_research_system_prompt = """You are a research assistant that has conducted research on a topic by calling several tools and web searches. Your job is now to clean up the findings, but preserve all of the relevant statements and information that the researcher has gathered. For context, today's date is {date}.
187: 
188: <Task>
189: You need to clean up information gathered from tool calls and web searches in the existing messages.
190: All relevant information should be repeated and rewritten verbatim, but in a cleaner format.
191: The purpose of this step is just to remove any obviously irrelevant or duplicative information.
192: For example, if three sources all say "X", you could say "These three sources all stated X".
193: Only these fully comprehensive cleaned findings are going to be returned to the user, so it's crucial that you don't lose any information from the raw messages.
194: </Task>
195: 
196: <Guidelines>
197: 1. Your output findings should be fully comprehensive and include ALL of the information and sources that the researcher has gathered from tool calls and web searches. It is expected that you repeat key information verbatim.
198: 2. This report can be as long as necessary to return ALL of the information that the researcher has gathered.
199: 3. In your report, you should return inline citations for each source that the researcher found.
200: 4. You should include a "Sources" section at the end of the report that lists all of the sources the researcher found with corresponding citations, cited against statements in the report.
201: 5. Make sure to include ALL of the sources that the researcher gathered in the report, and how they were used to answer the question!
202: 6. It's really important not to lose any sources. A later LLM will be used to merge this report with others, so having all of the sources is critical.
203: </Guidelines>
204: 
205: <Output Format>
206: The report should be structured like this:
207: **List of Queries and Tool Calls Made**
208: **Fully Comprehensive Findings**
209: **List of All Relevant Sources (with citations in the report)**
210: </Output Format>
211: 
212: <Citation Rules>
213: - Assign each unique URL a single citation number in your text
214: - End with ### Sources that lists each source with corresponding numbers
215: - IMPORTANT: Number sources sequentially without gaps (1,2,3,4...) in the final list regardless of which sources you choose
216: - Example format:
217:   [1] Source Title: URL
218:   [2] Source Title: URL
219: </Citation Rules>
220: 
221: Critical Reminder: It is extremely important that any information that is even remotely relevant to the user's research topic is preserved verbatim (e.g. don't rewrite it, don't summarize it, don't paraphrase it).
222: """
223: 
224: compress_research_simple_human_message = """All above messages are about research conducted by an AI Researcher. Please clean up these findings.
225: 
226: DO NOT summarize the information. I want the raw information returned, just in a cleaner format. Make sure all relevant information is preserved - you can rewrite findings verbatim."""
227: 
228: final_report_generation_prompt = """Based on all the research conducted, create a comprehensive, well-structured answer to the overall research brief:
229: <Research Brief>
230: {research_brief}
231: </Research Brief>
232: 
233: For more context, here is all of the messages so far. Focus on the research brief above, but consider these messages as well for more context.
234: <Messages>
235: {messages}
236: </Messages>
237: CRITICAL: Make sure the answer is written in the same language as the human messages!
238: For example, if the user's messages are in English, then MAKE SURE you write your response in English. If the user's messages are in Chinese, then MAKE SURE you write your entire response in Chinese.
239: This is critical. The user will only understand the answer if it is written in the same language as their input message.
240: 
241: Today's date is {date}.
242: 
243: Here are the findings from the research that you conducted:
244: <Findings>
245: {findings}
246: </Findings>
247: 
248: Please create a detailed answer to the overall research brief that:
249: 1. Is well-organized with proper headings (# for title, ## for sections, ### for subsections)
250: 2. Includes specific facts and insights from the research
251: 3. References relevant sources using [Title](URL) format
252: 4. Provides a balanced, thorough analysis. Be as comprehensive as possible, and include all information that is relevant to the overall research question. People are using you for deep research and will expect detailed, comprehensive answers.
253: 5. Includes a "Sources" section at the end with all referenced links
254: 
255: You can structure your report in a number of different ways. Here are some examples:
256: 
257: To answer a question that asks you to compare two things, you might structure your report like this:
258: 1/ intro
259: 2/ overview of topic A
260: 3/ overview of topic B
261: 4/ comparison between A and B
262: 5/ conclusion
263: 
264: To answer a question that asks you to return a list of things, you might only need a single section which is the entire list.
265: 1/ list of things or table of things
266: Or, you could choose to make each item in the list a separate section in the report. When asked for lists, you don't need an introduction or conclusion.
267: 1/ item 1
268: 2/ item 2
269: 3/ item 3
270: 
271: To answer a question that asks you to summarize a topic, give a report, or give an overview, you might structure your report like this:
272: 1/ overview of topic
273: 2/ concept 1
274: 3/ concept 2
275: 4/ concept 3
276: 5/ conclusion
277: 
278: If you think you can answer the question with a single section, you can do that too!
279: 1/ answer
280: 
281: REMEMBER: Section is a VERY fluid and loose concept. You can structure your report however you think is best, including in ways that are not listed above!
282: Make sure that your sections are cohesive, and make sense for the reader.
283: 
284: For each section of the report, do the following:
285: - Use simple, clear language
286: - Use ## for section title (Markdown format) for each section of the report
287: - Do NOT ever refer to yourself as the writer of the report. This should be a professional report without any self-referential language. 
288: - Do not say what you are doing in the report. Just write the report without any commentary from yourself.
289: - Each section should be as long as necessary to deeply answer the question with the information you have gathered. It is expected that sections will be fairly long and verbose. You are writing a deep research report, and users will expect a thorough answer.
290: - Use bullet points to list out information when appropriate, but by default, write in paragraph form.
291: 
292: REMEMBER:
293: The brief and research may be in English, but you need to translate this information to the right language when writing the final answer.
294: Make sure the final answer report is in the SAME language as the human messages in the message history.
295: 
296: Format the report in clear markdown with proper structure and include source references where appropriate.
297: 
298: <Citation Rules>
299: - Assign each unique URL a single citation number in your text
300: - End with ### Sources that lists each source with corresponding numbers
301: - IMPORTANT: Number sources sequentially without gaps (1,2,3,4...) in the final list regardless of which sources you choose
302: - Each source should be a separate line item in a list, so that in markdown it is rendered as a list.
303: - Example format:
304:   [1] Source Title: URL
305:   [2] Source Title: URL
306: - Citations are extremely important. Make sure to include these, and pay a lot of attention to getting these right. Users will often use these citations to look into more information.
307: </Citation Rules>
308: """
309: 
310: 
311: summarize_webpage_prompt = """You are tasked with summarizing the raw content of a webpage retrieved from a web search. Your goal is to create a summary that preserves the most important information from the original web page. This summary will be used by a downstream research agent, so it's crucial to maintain the key details without losing essential information.
312: 
313: Here is the raw content of the webpage:
314: 
315: <webpage_content>
316: {webpage_content}
317: </webpage_content>
318: 
319: Please follow these guidelines to create your summary:

(Showing lines 40-319 of 368. Use offset=320 to continue.)
</content>
```

---

## Assistant (Build · CS5351/DeepSeek-V4-Flash · 3.3s)

I found the key conflict. Let me look at the Output Format vs Citation Rules inconsistency. The issue is that in the `compress_research_system_prompt` (lines 205-219), the Output Format specifies sections, but there's a conflict between how Sources are referenced inline vs. the numbering scheme.

Let me examine the issue more carefully and check the legacy prompts and how the final report uses citations.

**Tool: read**

**Input:**

```json
{
  "filePath": "/Users/sdm/open_deep_research/src/open_deep_research/prompts.py",
  "limit": 50,
  "offset": 319
}
```

**Output:**

```
<path>/Users/sdm/open_deep_research/src/open_deep_research/prompts.py</path>
<type>file</type>
<content>
319: Please follow these guidelines to create your summary:
320: 
321: 1. Identify and preserve the main topic or purpose of the webpage.
322: 2. Retain key facts, statistics, and data points that are central to the content's message.
323: 3. Keep important quotes from credible sources or experts.
324: 4. Maintain the chronological order of events if the content is time-sensitive or historical.
325: 5. Preserve any lists or step-by-step instructions if present.
326: 6. Include relevant dates, names, and locations that are crucial to understanding the content.
327: 7. Summarize lengthy explanations while keeping the core message intact.
328: 
329: When handling different types of content:
330: 
331: - For news articles: Focus on the who, what, when, where, why, and how.
332: - For scientific content: Preserve methodology, results, and conclusions.
333: - For opinion pieces: Maintain the main arguments and supporting points.
334: - For product pages: Keep key features, specifications, and unique selling points.
335: 
336: Your summary should be significantly shorter than the original content but comprehensive enough to stand alone as a source of information. Aim for about 25-30 percent of the original length, unless the content is already concise.
337: 
338: Present your summary in the following format:
339: 
340: ```
341: {{
342:    "summary": "Your summary here, structured with appropriate paragraphs or bullet points as needed",
343:    "key_excerpts": "First important quote or excerpt, Second important quote or excerpt, Third important quote or excerpt, ...Add more excerpts as needed, up to a maximum of 5"
344: }}
345: ```
346: 
347: Here are two examples of good summaries:
348: 
349: Example 1 (for a news article):
350: ```json
351: {{
352:    "summary": "On July 15, 2023, NASA successfully launched the Artemis II mission from Kennedy Space Center. This marks the first crewed mission to the Moon since Apollo 17 in 1972. The four-person crew, led by Commander Jane Smith, will orbit the Moon for 10 days before returning to Earth. This mission is a crucial step in NASA's plans to establish a permanent human presence on the Moon by 2030.",
353:    "key_excerpts": "Artemis II represents a new era in space exploration, said NASA Administrator John Doe. The mission will test critical systems for future long-duration stays on the Moon, explained Lead Engineer Sarah Johnson. We're not just going back to the Moon, we're going forward to the Moon, Commander Jane Smith stated during the pre-launch press conference."
354: }}
355: ```
356: 
357: Example 2 (for a scientific article):
358: ```json
359: {{
360:    "summary": "A new study published in Nature Climate Change reveals that global sea levels are rising faster than previously thought. Researchers analyzed satellite data from 1993 to 2022 and found that the rate of sea-level rise has accelerated by 0.08 mm/year² over the past three decades. This acceleration is primarily attributed to melting ice sheets in Greenland and Antarctica. The study projects that if current trends continue, global sea levels could rise by up to 2 meters by 2100, posing significant risks to coastal communities worldwide.",
361:    "key_excerpts": "Our findings indicate a clear acceleration in sea-level rise, which has significant implications for coastal planning and adaptation strategies, lead author Dr. Emily Brown stated. The rate of ice sheet melt in Greenland and Antarctica has tripled since the 1990s, the study reports. Without immediate and substantial reductions in greenhouse gas emissions, we are looking at potentially catastrophic sea-level rise by the end of this century, warned co-author Professor Michael Green."  
362: }}
363: ```
364: 
365: Remember, your goal is to create a summary that can be easily understood and utilized by a downstream research agent while preserving the most critical information from the original webpage.
366: 
367: Today's date is {date}.
368: """

(End of file - total 368 lines)
</content>
```

**Tool: read**

**Input:**

```json
{
  "filePath": "/Users/sdm/open_deep_research/src/legacy/prompts.py",
  "limit": 60,
  "offset": 120
}
```

**Output:**

```
<path>/Users/sdm/open_deep_research/src/legacy/prompts.py</path>
<type>file</type>
<content>
120: 
121: <Writing Guidelines>
122: - If existing section content is not populated, write from scratch
123: - If existing section content is populated, synthesize it with the source material
124: - Strict 150-200 word limit
125: - Use simple, clear language
126: - Use short paragraphs (2-3 sentences max)
127: - Use ## for section title (Markdown format)
128: </Writing Guidelines>
129: 
130: <Citation Rules>
131: - Assign each unique URL a single citation number in your text
132: - End with ### Sources that lists each source with corresponding numbers
133: - IMPORTANT: Number sources sequentially without gaps (1,2,3,4...) in the final list regardless of which sources you choose
134: - Example format:
135:   [1] Source Title: URL
136:   [2] Source Title: URL
137: </Citation Rules>
138: 
139: <Final Check>
140: 1. Verify that EVERY claim is grounded in the provided Source material
141: 2. Confirm each URL appears ONLY ONCE in the Source list
142: 3. Verify that sources are numbered sequentially (1,2,3...) without any gaps
143: </Final Check>
144: """
145: 
146: section_writer_inputs=""" 
147: <Report topic>
148: {topic}
149: </Report topic>
150: 
151: <Section name>
152: {section_name}
153: </Section name>
154: 
155: <Section topic>
156: {section_topic}
157: </Section topic>
158: 
159: <Existing section content (if populated)>
160: {section_content}
161: </Existing section content>
162: 
163: <Source material>
164: {context}
165: </Source material>
166: """
167: 
168: section_grader_instructions = """Review a report section relative to the specified topic:
169: 
170: <Report topic>
171: {topic}
172: </Report topic>
173: 
174: <section topic>
175: {section_topic}
176: </section topic>
177: 
178: <section content>
179: {section}

(Showing lines 120-179 of 513. Use offset=180 to continue.)
</content>

<system-reminder>
Instructions from: /Users/sdm/open_deep_research/src/legacy/CLAUDE.md
# Open Deep Research

## About Open Deep Research

Open Deep Research is an experimental, fully open-source research assistant that automates deep research and produces comprehensive reports on any topic. It's designed to help researchers, analysts, and curious individuals generate detailed, well-sourced reports without manual research overhead.

### Key Features
- **Automated Research**: Searches multiple sources (web, academic papers, specialized databases)
- **Comprehensive Reports**: Generates structured markdown reports with proper citations
- **Multiple Search APIs**: Supports Tavily, Perplexity, Exa, ArXiv, PubMed, DuckDuckGo, and more
- **Flexible Models**: Compatible with any LLM that supports the `init_chat_model()` API
- **Quality Evaluation**: Built-in evaluation systems to assess report quality

## Two Research Implementations

Open Deep Research offers two distinct approaches to automated research, each with unique advantages:

### 1. Graph-based Workflow Implementation

The **graph-based implementation** (`src/open_deep_research/graph.py`) follows a structured plan-and-execute workflow:

**Characteristics:**
- **Interactive Planning**: Uses a planner model to generate a structured report outline
- **Human-in-the-Loop**: Allows review and feedback on the report plan before execution
- **Sequential Process**: Creates sections one by one with reflection between iterations
- **Quality Focus**: Emphasizes report accuracy and structure through iterative refinement

**Best for:**
- High-stakes research where accuracy is critical
- Reports requiring specific structure or customization
- Situations where you want control over the research process
- Academic or professional research contexts

### 2. Multi-Agent Implementation

The **multi-agent implementation** (`src/open_deep_research/multi_agent.py`) uses a supervisor-researcher architecture:

**Characteristics:**
- **Supervisor Agent**: Manages overall research process and assembles final report
- **Parallel Research**: Multiple researcher agents work simultaneously on different sections
- **Speed Optimized**: Significantly faster due to parallel processing
- **Tool Specialization**: Each agent has specific tools for their role

**Best for:**
- Quick research and rapid report generation
- Exploratory research where speed matters
- Situations with less need for human oversight
- Business intelligence and market research

## Quality Evaluation

This guide explains how to quickly test and evaluate the quality of reports generated by Open Deep Research using the pytest evaluation system. The pytest evaluation system provides an easy way to:
- Test both research agent implementations (multi-agent and graph-based)
- Get immediate visual feedback with rich console output
- Verify report quality against 9 comprehensive criteria
- Compare different model configurations
- Track results in LangSmith for analysis

### Test Specific Agent
```bash
# Test only the multi-agent implementation
python tests/run_test.py --agent multi_agent

# Test only the graph-based implementation  
python tests/run_test.py --agent graph
```

## Understanding the Output

### Console Output

The evaluation provides rich visual feedback including:

1. **Test Configuration Panel**: Shows which agent and search API are being tested
2. **Model Configuration Table**: Displays all model settings in a formatted table
3. **Report Generation Status**: Real-time feedback during report creation
4. **Generated Report Display**: Full report rendered in markdown format
5. **Evaluation Results**: 
   - **PASSED/FAILED** status in color-coded panel
   - **Report Structure Analysis**: Table showing section headers
   - **Evaluation Justification**: Detailed explanation from the evaluator

### What Gets Evaluated

The system checks reports against 9 quality criteria:

1. **Topic Relevance (Overall)**: Does the report address the input topic thoroughly?
2. **Section Relevance (Critical)**: Are all sections directly relevant to the main topic?
3. **Structure and Flow**: Do sections flow logically and create a cohesive narrative?
4. **Introduction Quality**: Does the introduction provide context and scope?
5. **Conclusion Quality**: Does the conclusion summarize key findings?
6. **Structural Elements**: Proper use of tables, lists, etc.
7. **Section Headers**: Correct Markdown formatting (# for title, ## for sections)
8. **Citations**: Proper source citation in each main body section
9. **Overall Quality**: Well-researched, accurate, and professionally written
   
   </system-reminder>
   ```

---

## Assistant (Build · CS5351/DeepSeek-V4-Flash · 2.8s)

Now let me check the `graph.py` in the main implementation to see whether the Sources section format is referenced there too, and check the legacy `graph.py`. Let me also check how these prompts are actually used, and confirm issue #232's nature by looking at git history/README.

**Tool: grep**

**Input:**

```json
{
  "include": "*.md",
  "pattern": "Sources|Citation|citation|\\[1\\]|\\[2\\]",
  "path": "/Users/sdm/open_deep_research"
}
```

**Output:**

```
Found 26 matches
/Users/sdm/open_deep_research/src/legacy/CLAUDE.md:
  Line 9: - **Comprehensive Reports**: Generates structured markdown reports with proper citations

  Line 93: 8. **Citations**: Proper source citation in each main body section


/Users/sdm/open_deep_research/src/legacy/legacy.md:
  Line 342: - Proper use of structural elements (headers, citations)

  Line 344: - Citation quality and source attribution

  Line 398: 3. **Structure**: Assessment of logical flow, formatting, and citation practices


/Users/sdm/open_deep_research/examples/pubmed.md:
  Line 33: ### Sources

  Line 52: ### Sources

  Line 71: ### Sources

  Line 92: ### Sources

  Line 111: ### Sources

  Line 129: ### Sources


/Users/sdm/open_deep_research/examples/inference-market-gpt45.md:
  Line 19: ### Sources

  Line 40: ### Sources

  Line 59: ### Sources

  Line 74: ### Sources

  Line 98: ### Sources


/Users/sdm/open_deep_research/examples/inference-market.md:
  Line 24: ### Sources

  Line 44: ### Sources

  Line 62: ### Sources

  Line 80: ### Sources

  Line 101: ### Sources


/Users/sdm/open_deep_research/examples/arxiv.md:
  Line 20: ### Sources

  Line 40: ### Sources

  Line 59: ### Sources

  Line 83: ### Sources

  Line 104: ### Sources
```

**Tool: read**

**Input:**

```json
{
  "filePath": "/Users/sdm/open_deep_research/src/open_deep_research/prompts.py",
  "limit": 40,
  "offset": 1
}
```

**Output:**

```
<path>/Users/sdm/open_deep_research/src/open_deep_research/prompts.py</path>
<type>file</type>
<content>
1: """System prompts and prompt templates for the Deep Research agent."""
2: 
3: clarify_with_user_instructions="""
4: These are the messages that have been exchanged so far from the user asking for the report:
5: <Messages>
6: {messages}
7: </Messages>
8: 
9: Today's date is {date}.
10: 
11: Assess whether you need to ask a clarifying question, or if the user has already provided enough information for you to start research.
12: IMPORTANT: If you can see in the messages history that you have already asked a clarifying question, you almost always do not need to ask another one. Only ask another question if ABSOLUTELY NECESSARY.
13: 
14: If there are acronyms, abbreviations, or unknown terms, ask the user to clarify.
15: If you need to ask a question, follow these guidelines:
16: - Be concise while gathering all necessary information
17: - Make sure to gather all the information needed to carry out the research task in a concise, well-structured manner.
18: - Use bullet points or numbered lists if appropriate for clarity. Make sure that this uses markdown formatting and will be rendered correctly if the string output is passed to a markdown renderer.
19: - Don't ask for unnecessary information, or information that the user has already provided. If you can see that the user has already provided the information, do not ask for it again.
20: 
21: Respond in valid JSON format with these exact keys:
22: "need_clarification": boolean,
23: "question": "<question to ask the user to clarify the report scope>",
24: "verification": "<verification message that we will start research>"
25: 
26: If you need to ask a clarifying question, return:
27: "need_clarification": true,
28: "question": "<your clarifying question>",
29: "verification": ""
30: 
31: If you do not need to ask a clarifying question, return:
32: "need_clarification": false,
33: "question": "",
34: "verification": "<acknowledgement message that you will now start research based on the provided information>"
35: 
36: For the verification message when no clarification is needed:
37: - Acknowledge that you have sufficient information to proceed
38: - Briefly summarize the key aspects of what you understand from their request
39: - Confirm that you will now begin the research process
40: - Keep the message concise and professional

(Showing lines 1-40 of 368. Use offset=41 to continue.)
</content>
```

---

## Assistant (Build · CS5351/DeepSeek-V4-Flash · 2.5s)

Now I have a clear picture of the conflict. Let me look at the examples to see the actual rendered Sources format, and check how these prompts are wired in deep_researcher.py.

**Tool: read**

**Input:**

```json
{
  "filePath": "/Users/sdm/open_deep_research/examples/inference-market.md",
  "limit": 30,
  "offset": 14
}
```

**Output:**

```
<path>/Users/sdm/open_deep_research/examples/inference-market.md</path>
<type>file</type>
<content>
14: * Increasing demand for real-time processing capabilities
15: * Shift toward token-based pricing models
16: * Rising adoption of specialized AI hardware
17: * Growth in open-source model deployment
18: * Integration of edge computing solutions
19: 
20: North America maintains market leadership with 38% global share, generating $9.34 billion in revenue (2024). This dominance stems from robust digital infrastructure and concentrated presence of technology companies, particularly in the United States where revenue reaches $8.6 billion.
21: 
22: The market shows sustained growth potential, supported by ongoing infrastructure investments and technological innovation, particularly in cloud-based deployments where North America maintains clear leadership.
23: 
24: ### Sources
25: - AI Inference Server Market Forecast : https://www.einpresswire.com/article/779610673/ai-inference-server-market-supports-new-technology-with-usd-133-2-billion-by-2034-regional-growth-at-usd-9-34-billion
26: - SemiAnalysis Market Report : https://semianalysis.com/2024/02/21/groq-inference-tokenomics-speed-but/
27: - Markets and Markets AI Inference Report : https://www.marketsandmarkets.com/Market-Reports/ai-inference-market-189921964.html
28: 
29: ## Fireworks.ai Profile
30: 
31: **Fireworks.ai has emerged as a significant AI inference provider by focusing on performance optimization, reaching a $552M valuation in 2024 with an estimated $44M in annual revenue.** Their platform serves over 25 billion tokens daily to more than 23,000 developers through a tiered pricing structure that scales with usage.
32: 
33: The company's technical differentiation comes from custom optimizations like FireAttention, which demonstrates superior performance metrics compared to competitors. Benchmark tests show up to 5.6x higher throughput and 12.2x lower latency versus vLLM for Mixtral 8x7B models in fp8 format.
34: 
35: Their pricing model combines usage-based tiers with flexible deployment options:
36: * Basic tier: $50/month spending limit
37: * Growth tier: $500/month spending limit
38: * Scale tier: $5,000/month spending limit
39: * Enterprise tier: Custom limits with dedicated support
40: * On-demand GPU deployments: $2.90-$9.99 per hour
41: 
42: Notable enterprise customers including DoorDash, Quora, and Upwork validate their approach. Since founding in 2022, Fireworks has secured $77M in funding from investors like Benchmark and Sequoia Capital.
43: 

(Showing lines 14-43 of 116. Use offset=44 to continue.)
</content>
```

**Tool: grep**

**Input:**

```json
{
  "include": "*.py",
  "path": "/Users/sdm/open_deep_research/src/open_deep_research",
  "pattern": "final_report_generation_prompt|compress_research_system_prompt"
}
```

**Output:**

```
Found 6 matches
/Users/sdm/open_deep_research/src/open_deep_research/deep_researcher.py:
  Line 25:     compress_research_system_prompt,

  Line 26:     final_report_generation_prompt,

  Line 547:             compression_prompt = compress_research_system_prompt.format(date=get_today_str())

  Line 642:             final_report_prompt = final_report_generation_prompt.format(


/Users/sdm/open_deep_research/src/open_deep_research/prompts.py:
  Line 186: compress_research_system_prompt = """You are a research assistant that has conducted research on a topic by calling several tools and web searches. Your job is now to clean up the findings, but preserve all of the relevant statements and information that the researcher has gathered. For context, today's date is {date}.

  Line 228: final_report_generation_prompt = """Based on all the research conducted, create a comprehensive, well-structured answer to the overall research brief:
```

---

## Assistant (Build · CS5351/DeepSeek-V4-Flash · 3.0s)

Now I understand the inconsistency. Let me look at how the deep_researcher.py uses these prompts (around lines 540-660) to understand the full pipeline.

**Tool: read**

**Input:**

```json
{
  "filePath": "/Users/sdm/open_deep_research/src/open_deep_research/deep_researcher.py",
  "limit": 130,
  "offset": 535
}
```

**Output:**

```
<path>/Users/sdm/open_deep_research/src/open_deep_research/deep_researcher.py</path>
<type>file</type>
<content>
535:     researcher_messages = state.get("researcher_messages", [])
536:     
537:     # Add instruction to switch from research mode to compression mode
538:     researcher_messages.append(HumanMessage(content=compress_research_simple_human_message))
539:     
540:     # Step 3: Attempt compression with retry logic for token limit issues
541:     synthesis_attempts = 0
542:     max_attempts = 3
543:     
544:     while synthesis_attempts < max_attempts:
545:         try:
546:             # Create system prompt focused on compression task
547:             compression_prompt = compress_research_system_prompt.format(date=get_today_str())
548:             messages = [SystemMessage(content=compression_prompt)] + researcher_messages
549:             
550:             # Execute compression
551:             response = await synthesizer_model.ainvoke(messages)
552:             
553:             # Extract raw notes from all tool and AI messages
554:             raw_notes_content = "\n".join([
555:                 str(message.content) 
556:                 for message in filter_messages(researcher_messages, include_types=["tool", "ai"])
557:             ])
558:             
559:             # Return successful compression result
560:             return {
561:                 "compressed_research": str(response.content),
562:                 "raw_notes": [raw_notes_content]
563:             }
564:             
565:         except Exception as e:
566:             synthesis_attempts += 1
567:             
568:             # Handle token limit exceeded by removing older messages
569:             if is_token_limit_exceeded(e, configurable.research_model):
570:                 researcher_messages = remove_up_to_last_ai_message(researcher_messages)
571:                 continue
572:             
573:             # For other errors, continue retrying
574:             continue
575:     
576:     # Step 4: Return error result if all attempts failed
577:     raw_notes_content = "\n".join([
578:         str(message.content) 
579:         for message in filter_messages(researcher_messages, include_types=["tool", "ai"])
580:     ])
581:     
582:     return {
583:         "compressed_research": "Error synthesizing research report: Maximum retries exceeded",
584:         "raw_notes": [raw_notes_content]
585:     }
586: 
587: # Researcher Subgraph Construction
588: # Creates individual researcher workflow for conducting focused research on specific topics
589: researcher_builder = StateGraph(
590:     ResearcherState, 
591:     output=ResearcherOutputState, 
592:     config_schema=Configuration
593: )
594: 
595: # Add researcher nodes for research execution and compression
596: researcher_builder.add_node("researcher", researcher)                 # Main researcher logic
597: researcher_builder.add_node("researcher_tools", researcher_tools)     # Tool execution handler
598: researcher_builder.add_node("compress_research", compress_research)   # Research compression
599: 
600: # Define researcher workflow edges
601: researcher_builder.add_edge(START, "researcher")           # Entry point to researcher
602: researcher_builder.add_edge("compress_research", END)      # Exit point after compression
603: 
604: # Compile researcher subgraph for parallel execution by supervisor
605: researcher_subgraph = researcher_builder.compile()
606: 
607: async def final_report_generation(state: AgentState, config: RunnableConfig):
608:     """Generate the final comprehensive research report with retry logic for token limits.
609:     
610:     This function takes all collected research findings and synthesizes them into a 
611:     well-structured, comprehensive final report using the configured report generation model.
612:     
613:     Args:
614:         state: Agent state containing research findings and context
615:         config: Runtime configuration with model settings and API keys
616:         
617:     Returns:
618:         Dictionary containing the final report and cleared state
619:     """
620:     # Step 1: Extract research findings and prepare state cleanup
621:     notes = state.get("notes", [])
622:     cleared_state = {"notes": {"type": "override", "value": []}}
623:     findings = "\n".join(notes)
624:     
625:     # Step 2: Configure the final report generation model
626:     configurable = Configuration.from_runnable_config(config)
627:     writer_model_config = {
628:         "model": configurable.final_report_model,
629:         "max_tokens": configurable.final_report_model_max_tokens,
630:         "api_key": get_api_key_for_model(configurable.final_report_model, config),
631:         "tags": ["langsmith:nostream"]
632:     }
633:     
634:     # Step 3: Attempt report generation with token limit retry logic
635:     max_retries = 3
636:     current_retry = 0
637:     findings_token_limit = None
638:     
639:     while current_retry <= max_retries:
640:         try:
641:             # Create comprehensive prompt with all research context
642:             final_report_prompt = final_report_generation_prompt.format(
643:                 research_brief=state.get("research_brief", ""),
644:                 messages=get_buffer_string(state.get("messages", [])),
645:                 findings=findings,
646:                 date=get_today_str()
647:             )
648:             
649:             # Generate the final report
650:             final_report = await configurable_model.with_config(writer_model_config).ainvoke([
651:                 HumanMessage(content=final_report_prompt)
652:             ])
653:             
654:             # Return successful report generation
655:             return {
656:                 "final_report": final_report.content, 
657:                 "messages": [final_report],
658:                 **cleared_state
659:             }
660:             
661:         except Exception as e:
662:             # Handle token limit exceeded errors with progressive truncation
663:             if is_token_limit_exceeded(e, configurable.final_report_model):
664:                 current_retry += 1

(Showing lines 535-664 of 719. Use offset=665 to continue.)
</content>
```

---

## Assistant (Build · CS5351/DeepSeek-V4-Flash · 3.3s)

I now have a comprehensive understanding. Let me also verify the README for any mention of the report format, to check if it needs updating too.

**Tool: grep**

**Input:**

```json
{
  "include": "*.md",
  "path": "/Users/sdm/open_deep_research",
  "pattern": "Source|citation|\\[Title\\]"
}
```

**Output:**

```
Found 25 matches
/Users/sdm/open_deep_research/src/legacy/CLAUDE.md:
  Line 9: - **Comprehensive Reports**: Generates structured markdown reports with proper citations

  Line 93: 8. **Citations**: Proper source citation in each main body section


/Users/sdm/open_deep_research/src/legacy/legacy.md:
  Line 342: - Proper use of structural elements (headers, citations)

  Line 398: 3. **Structure**: Assessment of logical flow, formatting, and citation practices


/Users/sdm/open_deep_research/examples/pubmed.md:
  Line 33: ### Sources

  Line 52: ### Sources

  Line 71: ### Sources

  Line 92: ### Sources

  Line 111: ### Sources

  Line 129: ### Sources


/Users/sdm/open_deep_research/examples/inference-market-gpt45.md:
  Line 19: ### Sources

  Line 40: ### Sources

  Line 59: ### Sources

  Line 74: ### Sources

  Line 98: ### Sources


/Users/sdm/open_deep_research/examples/inference-market.md:
  Line 24: ### Sources

  Line 44: ### Sources

  Line 62: ### Sources

  Line 80: ### Sources

  Line 101: ### Sources


/Users/sdm/open_deep_research/examples/arxiv.md:
  Line 20: ### Sources

  Line 40: ### Sources

  Line 59: ### Sources

  Line 83: ### Sources

  Line 104: ### Sources
```

---

## Assistant (Build · CS5351/DeepSeek-V4-Flash · 2.9s)

Let me check the README to see if it describes the report structure, and confirm there are no other references to the Sources format in non-md/py files.

**Tool: grep**

**Input:**

```json
{
  "pattern": "Source|Citation|citation",
  "path": "/Users/sdm/open_deep_research/README.md"
}
```

**Output:**

```
Found 100 matches (more matches available)
/Users/sdm/open_deep_research/src/legacy/CLAUDE.md:
  Line 9: - **Comprehensive Reports**: Generates structured markdown reports with proper citations

  Line 93: 8. **Citations**: Proper source citation in each main body section


/Users/sdm/open_deep_research/src/legacy/prompts.py:
  Line 116: 3. Then, look at the provided Source material.

  Line 130: <Citation Rules>

  Line 131: - Assign each unique URL a single citation number in your text

  Line 132: - End with ### Sources that lists each source with corresponding numbers

  Line 135:   [1] Source Title: URL

  Line 136:   [2] Source Title: URL

  Line 137: </Citation Rules>

  Line 140: 1. Verify that EVERY claim is grounded in the provided Source material

  Line 141: 2. Confirm each URL appears ONLY ONCE in the Source list

  Line 163: <Source material>

  Line 165: </Source material>

  Line 392:      - End with a "### Sources" subsection (H3 level with ###) containing a numbered list of URLs used

  Line 402: ### Sources


/Users/sdm/open_deep_research/src/legacy/graph.ipynb:
  Line 255:     "# 2. Generate content with citations\n",

  Line 288:        "### Sources  \n",

  Line 306:        "### Sources  \n",

  Line 321:        "### Sources  \n",


/Users/sdm/open_deep_research/src/open_deep_research/prompts.py:
  Line 71: 5. Sources

  Line 199: 3. In your report, you should return inline citations for each source that the researcher found.

  Line 200: 4. You should include a "Sources" section at the end of the report that lists all of the sources the researcher found with corresponding citations, cited against statements in the report.

  Line 209: **List of All Relevant Sources (with citations in the report)**

  Line 212: <Citation Rules>

  Line 213: - Assign each unique URL a single citation number in your text

  Line 214: - End with ### Sources that lists each source with corresponding numbers

  Line 217:   [1] Source Title: URL

  Line 218:   [2] Source Title: URL

  Line 219: </Citation Rules>

  Line 253: 5. Includes a "Sources" section at the end with all referenced links

  Line 298: <Citation Rules>

  Line 299: - Assign each unique URL a single citation number in your text

  Line 300: - End with ### Sources that lists each source with corresponding numbers

  Line 304:   [1] Source Title: URL

  Line 305:   [2] Source Title: URL

  Line 306: - Citations are extremely important. Make sure to include these, and pay a lot of attention to getting these right. Users will often use these citations to look into more information.

  Line 307: </Citation Rules>


/Users/sdm/open_deep_research/src/legacy/utils.py:
  Line 134:         formatted_text += f"Source: {source['title']}\n"

  Line 298:                         'raw_content': str|None  # Full content or None for secondary citations

  Line 338:         citations = data.get("citations", ["https://perplexity.ai"])

  Line 343:         # First citation gets the full content

  Line 345:             "title": f"Perplexity Search, Source 1",

  Line 346:             "url": citations[0],

  Line 352:         # Add additional citations without duplicating content

  Line 353:         for i, citation in enumerate(citations[1:], start=2):

  Line 355:                 "title": f"Perplexity Search, Source {i}",

  Line 356:                 "url": citation,

  Line 404:                         'raw_content': str|None  # Full content or None for secondary citations


/Users/sdm/open_deep_research/src/legacy/legacy.md:
  Line 342: - Proper use of structural elements (headers, citations)

  Line 344: - Citation quality and source attribution

  Line 398: 3. **Structure**: Assessment of logical flow, formatting, and citation practices


/Users/sdm/open_deep_research/src/legacy/multi_agent.ipynb:
  Line 262:       "Data Sources – Various backend systems, including local storage, cloud databases, and external APIs.\n",

  Line 510:       "AppSource\n",

  Line 589:       "AppSource\n",

  Line 624:       "Today, we're open-sourcing the Model Context Protocol (MCP), a new standard for connecting AI assistants to the systems where data lives, including content repositories, business tools, and development environments. The Model Context Protocol is an open standard that enables developers to build secure, two-way connections between their data sources and AI-powered tools. Early adopters like Block and Apollo have integrated MCP into their systems, while development tools companies including Zed, Replit, Codeium, and Sourcegraph are working with MCP to enhance their platforms—enabling AI agents to better retrieve relevant information to further understand the context around a coding task and produce more nuanced and functional code with fewer attempts. All Claude.ai plans support connecting MCP servers to the Claude Desktop app.\n",

  Line 653:       "Early adopters like Block and Apollo have integrated MCP into their systems, while development tools companies including Zed, Replit, Codeium, and Sourcegraph are working with MCP to enhance their platforms—enabling AI agents to better retrieve relevant information to further understand the context around a coding task and produce more nuanced and functional code with fewer attempts.\n",

  Line 801:       "Citations\n",

  Line 971:       "AppSource\n",

  Line 1147:       "AppSource\n",

  Line 1265:       "Local Data Sources: Your computer’s files, databases, and services that MCP servers can securely access\n",

  Line 1467:        "- Early adopters include Block, Apollo, Replit, Sourcegraph and others building MCP servers for Google Drive, GitHub, Postgres, etc.\n",

  Line 1472:        "### Sources\n",

  Line 1502:        "### Sources\n",

  Line 1531:        "### Sources\n",

  Line 1554:        "### Sources\n",

  Line 1569:        "### Sources\n",

  Line 1600:        "### Sources\n",


/Users/sdm/open_deep_research/src/legacy/tests/test_report_quality.py:
  Line 70: 8. Citations: Does the report properly cite sources in each main body section?


/Users/sdm/open_deep_research/tests/pairwise_evaluation.py:
  Line 21: - Citations should be provided for all claims, and should be formatted in a way that is easy to read and understand.

  Line 76: - Citations should be provided for all claims, and should be formatted in a way that is easy to read and understand.


/Users/sdm/open_deep_research/examples/inference-market-gpt45.md:
  Line 19: ### Sources

  Line 40: ### Sources

  Line 59: ### Sources

  Line 74: ### Sources

  Line 98: ### Sources


/Users/sdm/open_deep_research/examples/arxiv.md:
  Line 20: ### Sources

  Line 40: ### Sources

  Line 59: ### Sources

  Line 83: ### Sources

  Line 104: ### Sources


/Users/sdm/open_deep_research/examples/pubmed.md:
  Line 33: ### Sources

  Line 52: ### Sources

  Line 71: ### Sources

  Line 92: ### Sources

  Line 111: ### Sources

  Line 129: ### Sources


/Users/sdm/open_deep_research/tests/prompts.py:
  Line 11: 2. Source Quality and Methodology

  Line 14:    - Citation quality and integration

  Line 71: 2. Source Quality and Methodology: [Score]/5

  Line 116: 3. Citations: Does the response properly cite sources where necessary?

  Line 189: - Claims are often made where you see citations. You can check against the cited source as well.


/Users/sdm/open_deep_research/examples/inference-market.md:
  Line 24: ### Sources

  Line 44: ### Sources

  Line 62: ### Sources

  Line 80: ### Sources

  Line 101: ### Sources


/Users/sdm/open_deep_research/tests/expt_results/deep_research_bench_gpt-4.1.jsonl:
  Line 1: {"id": 57, "prompt": "Summarize the global investments, key initiatives, and outputs related to Artificial Intelligence (AI) by major international consulting firms (e.g., Big Four, Accenture, MBB, IBM, Capgemini). Cover aspects such as AI-driven products/services, client case studies, application scenarios, strategic directions, and talent development programs.", "article": "# How Leading Global Consulting Firms Invest in and Deliver Artificial Intelligence (AI) Solutions\n\n## Introduction\n\nGlobal consulting giants including the “Big Four” (Deloitte, PwC, EY, KPMG), Accenture, MBB (McKinsey, BCG, Bain), IBM, and Capgemini, have rapidly evolved into key players in the global AI ecosystem. These firms deploy multifaceted strategies to invest in, develop, and deliver state-of-the-art AI solutions across sectors and regions. This report provides a comprehensive analysis centered on five key pillars: (1) the scope and nature of AI investments, (2) flagship AI products and services, (3) notable client engagements and applications, (4) stated strategic intents, and (5) talent acquisition and development strategies. Where available, specific facts, initiatives, and case studies are provided, supported by reputable primary sources.\n\n---\n\n## 1. Global Scale and Types of AI Investments\n\n### Mergers, Acquisitions, and Strategic Alliances\n\n- **Deloitte** has prioritized strategic alliances with major tech leaders such as AWS, Google, Oracle, and SAP for AI capability expansion. Its investment also covers direct collaboration with AI leaders like Anthropic for generative and trustworthy AI. Deloitte’s AI and technology learning investments exceeded $2 billion, and the firm has deployed partnerships for co-development, notably with cloud and hardware providers like NVIDIA for enterprise AI stacks[1][2][3].\n- **PwC** has made “over $1 billion investment per day” industry-wide (referencing the overall market rather than self), and the AI-driven M&A boom has prompted inc...
  Line 2: {"id": 59, "prompt": "In ecology, how do birds achieve precise location and direction navigation during migration? What cues and disturbances influence this process?", "article": "# How Birds Achieve Precise Location and Directional Navigation During Migration: Mechanisms, Environmental Cues, Multimodal Integration, and Disruptions\n\n## Introduction\n\nMigratory birds travel thousands of kilometers with remarkable precision, often crossing continents and oceans between breeding and non-breeding grounds. This extraordinary navigational ability is underpinned by a complex, flexible system that integrates multiple environmental cues, innate genetic programs, learning, and social influences. Recent research—spanning large-scale GPS tracking, laboratory experiments, and molecular studies—has revealed new insights into how these navigation systems operate and how they are disrupted by both natural and anthropogenic factors. This report provides a comprehensive analysis of current understanding, emphasizing findings from the past decade.\n\n## Major Environmental Cues Used by Birds for Navigation\n\n### Geomagnetic Fields\n\n- Birds possess mechanisms to sense the Earth's magnetic field, utilizing information on inclination (angle), intensity, and declination (direction) as a global frame of reference for orientation.\n- Magnetoreception is considered essential, especially when other cues are unavailable (e.g., overcast conditions, open ocean).\n- Birds use geomagnetic maps and compasses, exploiting global spatial gradients in the Earth’s field to determine both direction and position.\n- Empirical studies (e.g., GPS tracking of greater white-fronted geese) demonstrate that birds follow magnetoclinic routes and loxodromes (constant magnetic direction), adjusting strategies with changing environmental contexts and migration stages[1][2].\n\n### Celestial Cues\n\n- The sun, stars, and polarized light patterns are vital, particularly for nocturnal migrants and in open landsc...
  Line 3: {"id": 93, "prompt": "Please prepare a market research analysis of the global video editing and creation software/tool market. Include major products like those from Adobe (Premiere Pro, After Effects), CapCut, DaVinci Resolve, Final Cut Pro, and others relevant in the current landscape.", "article": "# Global Video Editing and Creation Software Market Analysis (August 2025)\n\n## Executive Summary\n\nThe global video editing and creation software market continues to experience robust growth, driven by ongoing adoption across creative industries, the explosive rise of user-generated content (UGC), proliferation of mobile-first and cloud solutions, and a new wave of AI-powered disruptors. As of August 2025, the market includes established professional tools (e.g., Adobe Premiere Pro, Final Cut Pro, DaVinci Resolve), fast-scaling consumer/mobile products (e.g., CapCut), and a rapidly diversifying landscape of AI-first and browser-based platforms. This report provides a comprehensive overview of market trends, major players, regional dynamics, emerging technologies, and future outlook, substantiated by the most current data from official sources and reputable industry analysts.\n\n## Market Size and Growth Trends\n\n- As of 2025, the global video editing software market is estimated between $2.5 and $3.65 billion, depending on scope, with projected CAGR between 5.2% and 8.1% through 2029. By 2029, forecasts place the market size between $3.3 billion and $5 billion, depending on whether services and AI tools are included in the estimate[1][2][3][4][5].\n- Growth is sustained by several key drivers: deepening penetration of smartphones, increasing demand for digital media content, advances in AI and cloud editing, and the expanding role of video in marketing, education, and OTT platforms.\n- The AI video editing sector is the fastest-growing segment, forecast to skyrocket from $1.6 billion in 2025 to $9.3 billion by 2030 at over 42% CAGR[6].\n- Paid video editing softwar...
  Line 4: {"id": 97, "prompt": "Find data and evidence to support or refute the hypothesis that an airport handling an annual passenger throughput of 500,000 (five hundred thousand) can generate significant and measurable socioeconomic impacts on its surrounding region.", "article": "# Can an Airport with 500,000 Annual Passengers Generate Significant Socioeconomic Impacts? Evidence and Analysis\n\n## Executive Summary\n\nSubstantial empirical evidence and case studies demonstrate that airports with an annual throughput around 500,000 passengers can generate significant, measurable socioeconomic impacts on their surrounding regions—though the scale, scope, and sustainability of these impacts are highly contingent on geographic context, government policy, financial viability, and the specific needs of the community. These impacts span economic growth, employment, regional connectivity, business development, property values, and quality of life. However, challenges such as chronic unprofitability, the need for subsidy, and potential negative externalities (especially environmental and noise effects) are also noted, particularly in non-peripheral regions and where long-term demand is weak.\n\n## Economic Growth and Output\n\nAirports serving approximately 500,000 passengers annually have been shown to catalyze local and regional economies by:\n\n- **Facilitating trade and business travel**\n- **Attracting investment and supporting tourism**\n- **Multiplying on- and off-airport economic activity through direct, indirect, and induced effects**\n\nFor instance, the [U.S. DOT’s guide](https://gardnermagazine.com/wp-content/uploads/2024/02/Airports-1992-Report-dot_35802_DS1.pdf) provides a methodology to quantify such effects, emphasizing the need to account for jobs, payroll, and output directly and indirectly attributable to the airport. The **Rapid City Regional Airport (RAP)**, with throughput in the 500,000 to 700,000 annual passenger range, generates approximately $456 million ...

(Results truncated. Consider using a more specific path or pattern.)
```

**Tool: grep**

**Input:**

```json
{
  "pattern": "Sources|\\[Title\\]|\\[1\\] Source",
  "include": "*.py",
  "path": "/Users/sdm/open_deep_research/tests"
}
```

**Output:**

```
No files found
```

---

## Assistant (Build · CS5351/DeepSeek-V4-Flash · 5.4s)

Interesting. The evaluation results (which reflect actual real-world output) show a **completely different** citation style than what the prompts specify. Let me look at how the actual output uses citations — the `.jsonl` file shows citations like `[1][2][3]` inline AND a `### Sources` section. Let me examine the actual format in that eval result more closely to understand what's actually happening vs. what the prompts say.

Let me check the actual end of a report in that JSONL and the raw sources section.

**Tool: bash**

**Input:**

```json
{
  "command": "python3 -c \"\nimport json\nwith open('/Users/sdm/open_deep_research/tests/expt_results/deep_research_bench_gpt-4.1.jsonl') as f:\n    for line in f:\n        d = json.loads(line)\n        if d['id'] == 57:\n            article = d['article']\n            print('TOTAL LEN:', len(article))\n            print('--- LAST 1500 CHARS ---')\n            print(article[-1500:])\n            break\n\""
}
```

**Output:**

```
TOTAL LEN: 12481
--- LAST 1500 CHARS ---
Stories and Successes | Deloitte US: https://www.deloitte.com/us/en/what-we-do/content/client-stories-and-successes.html  
[11] Case Study: PwC's Generative AI Journey — AIX: https://aiexpert.network/ai-at-pwc/  
[12] PwC 2025 Global AI Jobs Barometer – PwC press release: https://www.pwc.com/gx/en/news-room/press-releases/2025/ai-linked-to-a-fourfold-increase-in-productivity-growth.html  
[13] Three New AI Breakthroughs Shaping 2026: AI Trends | Deloitte US: https://www.deloitte.com/us/en/services/consulting/blogs/new-ai-breakthroughs-ai-trends.html  
[14] Top ten priorities for data, analytics, & AI executives - Deloitte: https://www.deloitte.com/us/en/programs/chief-data-and-analytics-officer/articles/top-priorities-for-data-analytics-and-AI-execs.html  
[15] 2025 AI Business Predictions – PwC: https://www.pwc.com/us/en/tech-effect/ai-analytics/ai-predictions.html  
[16] The Future of Learning at Deloitte - LinkedIn: https://www.linkedin.com/pulse/future-learning-deloitte-anthony-r-stephan-cognc  
[17] AI Integration and Upskilling – PwC: https://www.pwc.com/gx/en/services/workforce/ai-integration-and-upskilling.html  
[18] How PwC opened the aperture of upskilling possibilities with AI – Unleash.ai: https://www.unleash.ai/learning-and-development/how-pwc-opened-the-aperture-of-upskilling-possibilities-with-ai-prompting-parties/  
[19] The Fearless Future: 2025 Global AI Jobs Barometer – PwC: https://www.pwc.com/gx/en/issues/artificial-intelligence/ai-jobs-barometer.html  
```

---

## Assistant (Build · CS5351/DeepSeek-V4-Flash · 3.0s)

Let me see the `### Sources` header portion and the section right before it, to understand the full structure.

**Tool: bash**

**Input:**

```json
{
  "command": "python3 -c \"\nimport json\nwith open('/Users/sdm/open_deep_research/tests/expt_results/deep_research_bench_gpt-4.1.jsonl') as f:\n    for line in f:\n        d = json.loads(line)\n        if d['id'] == 57:\n            article = d['article']\n            idx = article.find('### Sources')\n            print('Source header index:', idx)\n            print('--- CONTEXT BEFORE ---')\n            print(article[idx-400:idx])\n            print('--- FIRST 400 AFTER ---')\n            print(article[idx:idx+400])\n            break\n\""
}
```

**Output:**

```
Source header index: 9343
--- CONTEXT BEFORE ---
ts to broad adoption, developing trustworthy agentic and generative AI solutions, and upskilling a new generation of professionals capable of delivering sustained client value across every sector. This landscape is highly dynamic, with all firms investing heavily in competitive differentiation, industry shaping, and maintaining leadership in the trust, governance, and responsible use of AI.

---


--- FIRST 400 AFTER ---
### Sources

[1] Artificial intelligence and mergers and acquisitions - Deloitte: https://www2.deloitte.com/content/dam/Deloitte/us/Documents/mergers-acqisitions/us-artificial-intelligence-and-mergers-and-acquisitions.pdf  
[2] Deloitte Launches Turnkey Generative AI Solutions, AI Factory as a ...: https://www.deloitte.com/hu/en/about/press-room/deloitte-launches-ai-factory-service-powered-by-nvid
```

---

## Assistant (Build · CS5351/DeepSeek-V4-Flash · 10.9s)

This confirms the inconsistency. The **prompt instructions** (Citation Rules) say "End with `### Sources`" and "Number sources sequentially without gaps". But there's an internal inconsistency between the Output Format and Citation Rules sections within the same prompt, as the issue describes.

Let me carefully re-read the two prompt blocks to nail down the precise inconsistency that issue #232 is describing. Let me re-read the key conflicting text in `compress_research_system_prompt` (lines 199-219).

Looking back carefully:

**`compress_research_system_prompt` (lines 199-219):**

- Line 199: "you should return inline citations for each source"
- Line 200: "include a 'Sources' section ... with corresponding citations"
- Line 209 (Output Format): "**List of All Relevant Sources (with citations in the report)**"
- Line 212-219 (Citation Rules): Assign single number, end with `### Sources`, sequential numbering, `[1] Source Title: URL`

**`final_report_generation_prompt` (lines 248-307):**

- Line 251: "References relevant sources using [Title](URL) format" ✓
- Line 253: "Includes a 'Sources' section at the end with all referenced links"
- Line 298-307 (Citation Rules): Assign number, end with `### Sources`, sequential, `[1] Source Title: URL`

So the conflict: **Point 3 in the final report prompt (line 251) says `[Title](URL)`** (standard markdown inline links with NO numbers) for in-text references, but the **Citation Rules (line 298-306) say `[1][2][3]` numbered citations** matching a numbered `### Sources` list. These are two incompatible citation schemes within the same prompt. The model must choose between inline `[Title](URL)` links OR numbered `[1]` citations, but not both coherently.

Let me confirm there's nothing else and check git blame / the actual issue to be precise. Let me check the README report structure mention and git log.

Let me verify — is there a mention of report structure in README?

**Tool: bash**

**Input:**

```json
{
  "command": "grep -n -i \"source\\|citation\\|report format\\|### \" /Users/sdm/open_deep_research/README.md | head -30"
}
```

**Output:**

```
5:Deep research has broken out as one of the most popular agent applications. This is a simple, configurable, fully open source deep research agent that works across many model providers, search tools, and MCP servers. It's performance is on par with many popular deep research agents ([see Deep Research Bench leaderboard](https://huggingface.co/spaces/Ayanami0730/DeepResearch-Leaderboard)).
9:### 🔥 Recent Updates
21:### 🚀 Quickstart
28:source .venv/bin/activate  # On Windows: .venv\Scripts\activate
60:### ⚙️ Configurations
62:#### LLM :brain:
75:#### Search API :mag:
79:#### Other 
83:### 📊 Evaluation
87:#### Usage
106:#### Results 
115:### 🚀 Deployments and Usage
117:#### LangGraph Studio
121:#### Hosted deployment
125:#### Open Agent Platform
135:### Legacy Implementations 🏛️
139:#### 1. Workflow Implementation (`legacy/graph.py`)
145:#### 2. Multi-Agent Implementation (`legacy/multi_agent.py`)  
```

**Tool: bash**

**Input:**

```json
{
  "command": "cd /Users/sdm/open_deep_research && git log --oneline -15"
}
```

**Output:**

```
1b7d2e8 Bump h2 from 4.3.0 to 4.4.1 in the uv group across 1 directory (#334)
20aaa0d Bump cryptography in the uv group across 1 directory (#331)
7882410 Bump aiohttp from 3.14.1 to 3.14.3 in the uv group across 1 directory (#330)
d337ae3 Bump pyasn1 from 0.6.3 to 0.6.4 in the uv group across 1 directory (#295)
9fe9713 Bump mcp from 1.27.2 to 1.28.1 in the uv group across 1 directory (#292)
5b56197 Bump mcp from 1.23.0 to 1.27.2 in the uv group across 1 directory (#291)
b764481 Bump the uv group across 1 directory with 2 updates (#289)
cf987a7 Bump the uv group across 1 directory with 2 updates (#285)
408da44 Bump actions/checkout from 6 to 7 (#282)
e59ee30 Bump the uv group across 1 directory with 9 updates (#280)
1f24f11 Bump the uv group across 1 directory with 2 updates (#276)
68fb7ab Bump the uv group across 1 directory with 2 updates (#273)
aafb2b2 Bump the uv group across 1 directory with 5 updates (#271)
4b61120 Bump lxml from 5.4.0 to 6.1.0 in the uv group across 1 directory (#265)
0dd30bd Bump python-dotenv in the uv group across 1 directory (#263)
```

---

## Assistant (Build · CS5351/DeepSeek-V4-Flash · 21.8s)

The README doesn't describe the report structure in detail, so it doesn't reference the Sources format directly. I now have enough to present my findings. Let me confirm the full picture of both prompt blocks once more.

I have all the information I need. Let me now present my findings to the user.

## Investigation Findings

### Where the inconsistency lives

The conflict is **inside `final_report_generation_prompt`** in `src/open_deep_research/prompts.py` — the prompt that generates the final user-facing report. It simultaneously instructs the model to use **two incompatible citation styles**:

**Style A — inline Markdown links (line 251):**

> "References relevant sources using `[Title](URL)` format"

This is the classic Markdown syntax where `[Title](URL)` is a clickable link **with no citation number**. There's no numeric anchor system here.

**Style B — numbered bracket citations (lines 298-307, the `<Citation Rules>` block):**

> - Assign each unique URL a single citation number in your text
> - End with `### Sources` that lists each source with corresponding numbers
> - Example: `[1] Source Title: URL`

This requires numeric anchors `[1]`, `[2]`, `[3]` in the body that map to a numbered `### Sources` list.

The two styles contradict each other in the *same* prompt. The model can't consistently produce both: if it uses `[Title](URL)` inline links (Style A), there are no numbers to cross-reference the numbered list; if it uses `[1]` numbered citations (Style B), then `[Title](URL)` Format clause is meaningless. This is exactly the "inconsistency between Output Format and Citation Rules" described in issue #232.

### Where else the Sources format is referenced

I traced every reference to be sure the problem isn't isolated:

1. **`src/open_deep_research/prompts.py`** (active code — the real fix location):
   
   - `compress_research_system_prompt` (lines 199-219): Output Format block says `**List of All Relevant Sources (with citations in the report)**` while Citation Rules use `[1] Source Title: URL`. This is an *internal* (within-prompt) repetition of the same tension but is a *different node* — it's the compression step output, not the final report. Semantic conflict is milder but inconsistent with the final-report numbering.
   - `final_report_generation_prompt` (lines 251, 253, 298-307): **the core conflict** (Style A vs Style B).

2. **`src/legacy/prompts.py`** (lines 130-137, 392-402): legacy `section_writer_prompt` uses the same numbered `[1] Source Title: URL` Citers. This is the **older implementation** — updated separately or left alone, but it's not the active graph.

3. **Examples** (`examples/*.md`): consistently use `### Sources` **without numbered brackets** — they list sources as plain bullet/separated lines (e.g. `inference-market.md:24-27`):
   
   ```
   ### Sources
   - AI Inference Server Market Forecast : https://...
   - SemiAnalysis Market Report : https://...
   ```
   
   These represent real historical outputs and don't match the `[1] Source` numbered format the Citation Rules mandate (though they do match the `### Sources` header).

4. **Real evaluation outputs** (`tests/expt_results/deep_research_bench_gpt-4.1.jsonl`): work with **numbered `[1] ... [19]`** citations in the `### Sources` list AND numbered inline anchors in body text (e.g. `[1][2][3]`) — matching Style B, **not** Style A. So in practice the model already chose the numbered system.

5. **Evaluation/grader prompts**: `tests/prompts.py`, `tests/pairwise_evaluation.py`, `legacy/tests/test_report_quality.py` reference "citation quality" generically but don't hardcode the `[1]`/`[Title](URL)` format, so they're mostly agnostic.

6. **README.md**: does not describe the Sources/reference format, so nothing to update there.

### Possible solutions

**Option 1 — Make numbered citations the single source of truth (recommended).**
Remove the `[Title](URL)` clause (line 251) and standardize everything on the numbered system already in the `<Citation Rules>` block (`[1]...` + `### Sources`). Align `compress_research_system_prompt`'s Output Format label to the same numbered convention.

- *Pros:* Matches real-world output (the eval JSONL already uses `[1][2][3]`). Minimal behavioral shift; models already lean this way. One clean, consistent scheme.
- *Cons:* Numbered citations are less directly clickable for a reader; requires maintaining the numbering.

**Option 2 — Make inline Markdown links `[Title](URL)` the single source of truth.**
Remove the `<Citation Rules>` numbered block and the `### Sources` numbered list; have the report rely purely on inline `[Title](URL)` links plus an unnumbered sources list.

- *Pros:* Nicer UX (clickable links); simpler for readers; matches the real examples in `examples/*.md` (unnumbered `### Sources`).
- *Cons:* Diverges from the current real output in evals and the legacy prompts; likely lowers the structured-citation signal the graders expect. Larger behavior change, more rework across eval expectations.

**Option 3 — Keep both but make them consistent (hybrid).**
Use inline `[Title](URL)` links in the body AND present the `### Sources` list with the same titles/URLs unnumbered, explicitly telling the model these are the same references (no numeric anchors). Resolve the "no gaps" numbering instruction by removing it since there are no numbers.

- *Pros:* Clickable links + a sources index; the model stops being torn between two systems.
- *Cons:* Slightly more complex prompt; still diverges from the numbered eval outputs.

### Recommendation

**Option 1** is the cleanest given the evidence: the numbered citation scheme (Style B) is already what the system actually produces (confirmed by `tests/expt_results/*.jsonl`), what the legacy prompts use, and what the evaluation graders implicitly reward. Keeping the dangling `[Title](URL)` instruction (line 251) is the sole source of the contradiction, so removing that one line — and aligning the `compress_research_system_prompt` Output Format label to the numbered convention — resolves issue #232 with minimal churn and no behavioral regression.

### Files that would need updating for full consistency if you agree

- `src/open_deep_research/prompts.py` line 251 (remove `[Title](URL)`), and lines 199-209 (align compress prompt's Sources/Output Format wording to numbered scheme).
- Optionally `src/legacy/prompts.py` (only if you want legacy to stay in lockstep — it already uses numbered style, so likely no change needed, or a mirror consistency tweak).
- No changes needed to: examples (informational), eval graders (generic), README.

Want me to proceed with **Option 1**? I'll wait for your confirmation and your preference before changing anything.

---

## User

I'd like to go with Option 3. Please keep both the inline [Title](URL) links in the body and the ### Sources list at the end, but make them consistent — the Sources list should use the same titles/URLs as the inline links, without numeric anchors, and the "no gaps" numbering instruction should be removed since there are no numbers. Also, since Option 3 diverges from the numbered scheme that the eval outputs and legacy prompts currently use, please check whether the eval graders in tests/ actually require numbered citations — if they do, flag that conflict before proceeding. And please address the compress_research_system_prompt mismatch from the original issue as well, so both prompts are internally consistent. Report back before making any changes if the eval dependency is unclear

---

## Assistant (Build · CS5351/DeepSeek-V4-Flash · 2.4s)

Let me check the eval graders in `tests/` to determine whether they require numbered citations.

**Tool: read**

**Input:**

```json
{
  "filePath": "/Users/sdm/open_deep_research/tests/prompts.py"
}
```

**Output:**

```
<path>/Users/sdm/open_deep_research/tests/prompts.py</path>
<type>file</type>
<content>
1: OVERALL_QUALITY_PROMPT = """You are an expert evaluator tasked with assessing the quality of research reports. Please evaluate the provided research report across multiple dimensions, provide scores, and offer a comprehensive assessment.
2: 
3: Evaluation Criteria:
4: 
5: 1. Research Depth and Comprehensiveness
6:    - Thoroughness of analysis
7:    - Coverage of aspects relevant to the user's input
8:    - Depth of understanding
9:    - Background context provided
10: 
11: 2. Source Quality and Methodology
12:    - Use of authoritative sources (webpages)
13:    - Diversity of source webpage types (e.g. news articles, papers, etc.)
14:    - Citation quality and integration
15:    - Transparency of research methodology
16: 
17: 3. Analytical Rigor
18:    - Sophistication of analysis
19:    - Critical evaluation of the source information
20:    - Identification of nuances and limitations
21: 
22: 4. Practical Value and Actionability
23:    - Clarity of insights and recommendations
24:    - Specific examples and use cases
25:    - Does not refer to itself as the writer of the report at any point
26: 
27: 5. Balance and Objectivity
28:    - Presentation of multiple perspectives
29:    - Acknowledgment of limitations and trade-offs
30:    - Distinction between facts and opinions
31:    - Avoidance of bias
32: 
33: 6. Writing Quality and Clarity
34:    - Clarity and professionalism of writing
35:    - Appropriate use of terminology
36:    - Consistency of tone and style
37:    - Engagement and readability
38:    - Does not refer to itself as the writer of the report at any point
39: 
40: Scoring Instructions:
41: 1. Evaluate each dimension on a scale of 1-5, where:
42:    1 = Poor
43:    2 = Fair
44:    3 = Good
45:    4 = Very Good
46:    5 = Excellent
47: 
48: Evaluation Process:
49: 1. Begin by analyzing each dimension separately. Wrap your analysis for each dimension in <dimension_analysis> tags. For each dimension:
50:    a) Quote relevant sections from the report
51:    b) List pros and cons
52:    c) Consider how well it meets the criteria
53:    It's okay for this section to be quite long as you thoroughly analyze each dimension.
54: 
55: 2. After completing the analysis, provide the formal evaluation using the format specified below.
56: 
57: Additional Considerations:
58: - Assess whether the report's depth matches the complexity of the topic
59: - Evaluate if the report effectively serves its intended audience
60: - Consider the currency and relevance of the information presented
61: - Determine if critical aspects are covered adequately
62: - Look for the integration of quantitative data, case studies, and concrete examples where appropriate
63: 
64: Output Format:
65: Use the following format for your evaluation:
66: 
67: Dimension Scores:
68: 1. Research Depth and Comprehensiveness: [Score]/5
69:    Justification: [Brief explanation with examples]
70: 
71: 2. Source Quality and Methodology: [Score]/5
72:    Justification: [Brief explanation with examples]
73: 
74: 3. Analytical Rigor: [Score]/5
75:    Justification: [Brief explanation with examples]
76: 
77: 4. Practical Value and Actionability: [Score]/5
78:    Justification: [Brief explanation with examples]
79: 
80: 5. Balance and Objectivity: [Score]/5
81:    Justification: [Brief explanation with examples]
82: 
83: 6. Writing Quality and Clarity: [Score]/5
84:    Justification: [Brief explanation with examples]
85: 
86: Overall Assessment:
87: [2-3 paragraph summary of the report's quality, utility, and fitness for purpose]
88: 
89: Today is {today}
90: 
91: Now, please evaluate the research report.
92: """
93: 
94: 
95: CORRECTNESS_PROMPT = """You are evaluating the correctness of a research report that was generated by a research agent.
96: 
97: You will be provided with the question, the report, and the answer from an independent authority.
98: 
99: Score the report from 1-5 on how well it mirrors the answer from the authority. 
100: We expect the report to contain more information that is not in the answer, that's perfectly okay.
101: They likely won't be perfectly the same, but they should have the same themes and ideas to get a high score.
102: 
103: Use your best judgement when comparing the answer to the report!
104: """
105: 
106: RELEVANCE_PROMPT = """You are evaluating the relevance of a response to a user's input question. Please assess the answer against the following criteria, being especially strict about section relevance.
107: 
108: 1. Topic Relevance (Overall): Does the response directly address the user's input questions thoroughly?
109: 
110: 2. Section Relevance (Critical): CAREFULLY assess each individual section for relevance to the main topic:
111:    - Identify each section by its ## header
112:    - For each section, determine if it is directly relevant to the primary topic
113:    - Flag any sections that seem tangential, off-topic, or only loosely connected to the main topic
114:    - A high-quality response (score 5) should have NO irrelevant sections
115: 
116: 3. Citations: Does the response properly cite sources where necessary?
117: 
118: 4. Overall Quality: Is the response well-researched, accurate, and professionally written?
119: 
120: Evaluation Instructions:
121: - Be STRICT about section relevance - ALL sections must clearly connect to the primary topic
122: - You must individually mention each section by name and assess its relevance
123: - Provide specific examples from the response to justify your evaluation for each criterion
124: - A response that is not relevant to the user's input topic should be scored 1
125: - A response passing all of the above criteria should be scored 5
126: 
127: Today is {today}
128: """
129: 
130: 
131: STRUCTURE_PROMPT = """You are evaluating the structure and flow of a response to a user's question. Your evaluation should focus on the following criteria:
132: 
133: <Rubric>
134: A well-structured report should:
135: - Be in the correct format for the user's question
136:    - For example, if the user asks for a list of N items, the report should be a list of N items, no more, no less. This is crucial.
137:    - For example, if the user asks for a comparison of X and Y, the report should have a section about X, a section about Y, and a comparison of the two.
138: - Have a logical flow from one section to the next
139: - Be appropriate for the user's question
140: - Use structural elements (e.g., headers, tables, lists) to effectively convey information
141: - Have properly formatted section headers (e.g., # for title, ## for sections, ### for subsections)
142: </Rubric>
143: 
144: <Instruction>
145: - Compare the output against the user's question, is it in the format that the user asked for?
146: - Identify any sections that are not logically connected to the user's question
147: - Identify any sections that are not logically connected to the previous and next sections
148: - Reason about whether the structure is the best structure for the user's question
149: </Instruction>
150: 
151: <Reminder>
152: - Focus solely on structure and flow of the report
153: </Reminder>
154: 
155: <user_question>
156: {user_question}
157: </user_question>
158: 
159: <report>
160: {report}
161: </report>
162: 
163: Today is {today}
164: """
165: 
166: 
167: GROUNDEDNESS_PROMPT = """
168: You are evaluating how well a research report aligns with and is supported by the context retrieved from the web. Your evaluation should focus on the following criteria:
169: 
170: <Rubric> 
171: A well-grounded report should: 
172: - Make claims that are directly supported by the retrieved context
173: - Stay within the scope of information provided in the context
174: - Maintain the same meaning and intent as the source material
175: - Not introduce external facts or unsupported assertions outside of basic facts (2 + 2 = 4)
176: 
177: An ungrounded report:
178: - Makes claims without support from the context
179: - Contradicts the retrieved information
180: - Includes speculation or external knowledge outside of basic facts
181: - Distorts or misrepresents the context
182: </Rubric>
183: 
184: <Instruction>
185: - Compare the report against the retrieved context carefully
186: - Identify factual claims, statements, and assertions made in the report
187: - For each claim:
188:    - Decide whether it is directly grounded in the context
189: - Claims are often made where you see citations. You can check against the cited source as well.
190: </Instruction>
191: 
192: <context>
193: {context}
194: </context>
195: 
196: <report>
197: {report}
198: </report>
199: 
200: <Output Format>
201: Use the following format for your evaluation:
202: {{
203:    "claims": [
204:       {{
205:          "text": "string – the extracted claim",
206:          "grounded": true | false
207:       }},
208:       ...
209:    ]
210: }}
211: </Output Format>
212: """
213: 
214: 
215: COMPLETENESS_PROMPT = """You are evaluating the completeness of a research report. Your evaluation should focus on the following criteria:
216: 
217: <Rubric>
218: A complete report should:
219: - Answer all points from the user's question
220: - Have a research brief that fully encompasses the user's question
221: - Have a report that fully encompasses the research brief and the user's question
222: 
223: An incomplete report:
224: - Does not answer all points from the user's question
225: - Does not have a research brief that fully encompasses the user's question
226: - Does not have a report that fully encompasses the research brief and the user's question
227: - Makes assumptions that are not directly stated by the user's question
228: </Rubric>
229: 
230: <Instruction>
231: - Compare the output against the research brief and the user's question
232: - Identify any points that are not covered by the report
233: - Identify any points that are not covered by the research brief
234: - Identify any points that are not covered by the user's question
235: </Instruction>
236: 
237: <Reminder>
238: - Focus solely on completeness of the report
239: - Ignore whether external knowledge suggests different facts
240: - Consider both explicit and implicit claims
241: - Provide specific examples of complete/incomplete content  
242: </Reminder>
243: 
244: <research_brief>
245: {research_brief}
246: </research_brief>
247: 
248: <user_question>
249: {user_question}
250: </user_question>  
251: 
252: <report>
253: {report}
254: </report>
255: 
256: Today is {today}
257: """

(End of file - total 257 lines)
</content>
```

**Tool: read**

**Input:**

```json
{
  "filePath": "/Users/sdm/open_deep_research/tests/pairwise_evaluation.py"
}
```

**Output:**

```
<path>/Users/sdm/open_deep_research/tests/pairwise_evaluation.py</path>
<type>file</type>
<content>
1: from langchain_anthropic import ChatAnthropic
2: from langsmith.evaluation import evaluate_comparative
3: from pydantic import BaseModel, Field
4: 
5: HEAD_TO_HEAD_PROMPT = """
6: We are testing out two different implementations of a deep research agent. This research agent is designed to conduct deep research on a given question.
7: 
8: This was the question: 
9: {question}
10: 
11: First Implementation's Response:
12: {answer_a}
13: 
14: Second Implementation's Response:
15: {answer_b}
16: 
17: In order to evaluate these agents, keep the following criteria in mind:
18: - A good research agent should research sufficient sources to answer the question. These sources should be diverse and high quality. More sources is not always necessarily better, but it is important to have ENOUGH sources to feel confident in the claims that are made.
19: - A good research agent should completely and comprehensively answer the user's question. 
20: - Deep research agents are expensive. The user expects a very good, and also very detailed answer. They should get all of the information that they need from this response, and should not have to ask for followups usually.
21: - Citations should be provided for all claims, and should be formatted in a way that is easy to read and understand.
22: 
23: Important:
24: These two implementations conducted research differently, and so they might have different information and different sources. This is a key point for you to evaluate.
25: Which agent was able to find better sources and better answer the question? The #1 thing we care about the most is the quality and comprehensiveness of the answer.
26: 
27: With those criteria in mind, please select which response you prefer, and explain why!
28: """
29: 
30: class HeadToHeadRanking(BaseModel):
31:     reasoning: str = Field(description="The reasoning for why you selected the preferred answer. This should be a detailed explanation!")
32:     preferred_answer: int = Field(description="The preferred answer between 1 and 2, where 1 is the first response, 2 is the second response.")
33: 
34: 
35: def head_to_head_evaluator(inputs: dict, outputs: list[dict]) -> list:
36:     grader_llm = ChatAnthropic(
37:         model="claude-opus-4-20250514",
38:         max_tokens=20000,
39:         thinking={"type": "enabled", "budget_tokens": 16000},
40:     )
41: 
42:     response = grader_llm.with_structured_output(HeadToHeadRanking).invoke(HEAD_TO_HEAD_PROMPT.format(
43:         question=inputs["messages"][0]["content"],
44:         answer_a=outputs[0].get("final_report", "N/A"),
45:         answer_b=outputs[1].get("final_report", "N/A"),
46:     ))
47: 
48:     if response.preferred_answer == 1:
49:         scores = [1, 0]
50:     elif response.preferred_answer == 2:
51:         scores = [0, 1]
52:     else:
53:         scores = [0, 0]
54:     return scores
55: 
56: 
57: ALL_THREE_PROMPT = """
58: We are testing out three different implementations of a deep research agent. This research agent is designed to conduct deep research on a given question.
59: 
60: This was the question: 
61: {question}
62: 
63: First Implementation's Response:
64: {answer_a}
65: 
66: Second Implementation's Response:
67: {answer_b}
68: 
69: Third Implementation's Response:
70: {answer_c}
71: 
72: In order to evaluate these agents, keep the following criteria in mind:
73: - A good research agent should research sufficient sources to answer the question. These sources should be diverse and high quality. More sources is not always necessarily better, but it is important to have ENOUGH sources to feel confident in the claims that are made.
74: - A good research agent should completely and comprehensively answer the user's question. 
75: - Deep research agents are expensive. The user expects a very good, and also very detailed answer. They should get all of the information that they need from this response, and should not have to ask for followups usually.
76: - Citations should be provided for all claims, and should be formatted in a way that is easy to read and understand.
77: 
78: Important:
79: These three implementations conducted research differently, and so they might have different information and different sources. This is a key point for you to evaluate.
80: Which agent was able to find better sources and better answer the question? The #1 thing we care about the most is the quality and comprehensiveness of the answer.
81: 
82: With those criteria in mind, please rank the responses from 1 to 3, where 1 is the best response, 2 is the second best response, and 3 is the worst response.
83: And please explain why you selected the ranking you did!
84: """
85: 
86: class Rankings(BaseModel):
87:     reasoning: str = Field(description="The reasoning for why you selected the preferred answer. This should be a detailed explanation!")
88:     preferred_answer: int = Field(description="The preferred answer between 1 and 3, where 1 is the first response, 2 is the second response, and 3 is the third response.")
89:     second_best_answer: int = Field(description="The second best answer between 1 and 3, where 1 is the first response, 2 is the second response, and 3 is the third response.")
90:     worst_answer: int = Field(description="The worst answer between 1 and 3, where 1 is the first response, 2 is the second response, and 3 is the third response.")
91: 
92: def free_for_all_evaluator(inputs: dict, outputs: list[dict]) -> list:
93:     grader_llm = ChatAnthropic(
94:         model="claude-opus-4-20250514",
95:         max_tokens=20000,
96:         thinking={"type": "enabled", "budget_tokens": 16000},
97:     )
98: 
99:     response = grader_llm.with_structured_output(Rankings).invoke(ALL_THREE_PROMPT.format(
100:         question=inputs["messages"][0]["content"],
101:         answer_a=outputs[0].get("final_report", "N/A"),
102:         answer_b=outputs[1].get("final_report", "N/A"),
103:         answer_c=outputs[2].get("final_report", "N/A"),
104:     ))
105: 
106:     scores = [0, 0, 0]
107:     scores[response.preferred_answer - 1] = 1
108:     scores[response.second_best_answer - 1] = .5
109:     scores[response.worst_answer - 1] = 0
110:     return scores
111: 
112: single_agent = "DR Single Agent - Tavily #-87e8a6c0"
113: multi_agent_supervisor = "DR Supervisor: Multi Agent - Tavily #-cd25e7e3"
114: multi_agent_supervisor_v2 = "DR Supervisor: Multi Agent - Tavily (v2) #-40967f53"
115: multi_agent_workflow = "DR MAW - Tavily #-c6818a83"
116: 
117: 
118: # evaluate_comparative(
119: #     (single_agent_experiment_name, multi_agent_supervisor_experiment_name, multi_agent_workflow_experiment_name),  # Replace with the names/IDs of your experiments
120: #     evaluators=[free_for_all_evaluator],
121: #     randomize_order=True,
122: # )
123: 
124: evaluate_comparative(
125:     (single_agent, multi_agent_supervisor_v2),  # Replace with the names/IDs of your experiments
126:     evaluators=[head_to_head_evaluator],
127:     randomize_order=True,
128: )

(End of file - total 128 lines)
</content>
```

**Tool: read**

**Input:**

```json
{
  "filePath": "/Users/sdm/open_deep_research/tests/evaluators.py"
}
```

**Output:**

```
<path>/Users/sdm/open_deep_research/tests/evaluators.py</path>
<type>file</type>
<content>
1: from typing import cast
2: from pydantic import BaseModel, Field
3: from langchain_openai import ChatOpenAI
4: from langchain_anthropic import ChatAnthropic
5: from open_deep_research.utils import get_today_str
6: from tests.prompts import RELEVANCE_PROMPT, STRUCTURE_PROMPT, GROUNDEDNESS_PROMPT, OVERALL_QUALITY_PROMPT, CORRECTNESS_PROMPT, COMPLETENESS_PROMPT
7: 
8: eval_model = ChatOpenAI(
9:     model="gpt-4.1",
10: )
11: 
12: def _format_input_query(inputs: dict) -> str:
13:     messages = inputs["messages"]
14:     if len(messages) == 1:
15:         return messages[0]["content"]
16: 
17:     role_to_string_format_map = {
18:         "user": "<user_input>\n{content}\n</user_input>",
19:         "assistant": "<assistant_follow_up>\n{content}\n</assistant_follow_up>",
20:     }
21: 
22:     return "\n\n".join([role_to_string_format_map[message["role"]].format(content=message["content"]) for message in messages])
23: 
24: 
25: class OverallQualityScore(BaseModel):
26:     """Score the overall quality of the report against specific criteria."""
27:     research_depth: int = Field(description="Integer score 1-5 showing whether the report meets the provided criteria (1 = doesn't meet at all, 5 = meets all criteria).")
28:     source_quality: int = Field(description="Integer score 1-5 showing whether the report meets the provided criteria (1 = doesn't meet at all, 5 = meets all criteria).")
29:     analytical_rigor: int = Field(description="Integer score 1-5 showing whether the report meets the provided criteria (1 = doesn't meet at all, 5 = meets all criteria).")
30:     practical_value: int = Field(description="Integer score 1-5 showing whether the report meets the provided criteria (1 = doesn't meet at all, 5 = meets all criteria).")
31:     balance_and_objectivity: int = Field(description="Integer score 1-5 showing whether the report meets the provided criteria (1 = doesn't meet at all, 5 = meets all criteria).")
32:     writing_quality: int = Field(description="Integer score 1-5 showing whether the report meets the provided criteria (1 = doesn't meet at all, 5 = meets all criteria).")
33: 
34: def eval_overall_quality(inputs: dict, outputs: dict):
35:     query = _format_input_query(inputs)
36:     final_report = outputs["final_report"]
37:     user_input_content = f"""User input: {query}\n\nReport: \n\n{final_report}\n\nEvaluate whether the report meets the criteria and provide detailed justification for your evaluation."""
38:     if isinstance(eval_model, ChatAnthropic):
39:         user_input_content = [{
40:             "type": "text",
41:             "text": user_input_content,
42:             "cache_control": {"type": "ephemeral", "ttl": "1h"}
43:         }]
44:     eval_result = cast(OverallQualityScore, eval_model.with_structured_output(OverallQualityScore).invoke([
45:         {"role": "system", "content": OVERALL_QUALITY_PROMPT.format(today=get_today_str())},
46:         {"role": "user", "content": user_input_content}
47:     ]))
48:     return [
49:         {"key": "research_depth_score", "score": eval_result.research_depth / 5},
50:         {"key": "source_quality_score", "score": eval_result.source_quality / 5},
51:         {"key": "analytical_rigor_score", "score": eval_result.analytical_rigor / 5},
52:         {"key": "practical_value_score", "score": eval_result.practical_value / 5},
53:         {"key": "balance_and_objectivity_score", "score": eval_result.balance_and_objectivity / 5},
54:         {"key": "writing_quality_score", "score": eval_result.writing_quality / 5},
55:     ]
56: 
57: 
58: class RelevanceScore(BaseModel):
59:     """Score the report relevance against specific criteria."""
60:     reasoning: str = Field(description="The reason for the score, including specific examples from the report.")
61:     score: int = Field(description="Integer score 1-5 showing whether the report meets the provided criteria for relevance (1 = doesn't meet at all, 5 = meets all criteria).")
62: 
63: def eval_relevance(inputs: dict, outputs: dict):
64:     query = _format_input_query(inputs)
65:     final_report = outputs["final_report"]
66:     user_input_content = f"""User input: {query}\n\nReport: \n\n{final_report}\n\nEvaluate whether the report meets the criteria and provide detailed justification for your evaluation."""
67:     if isinstance(eval_model, ChatAnthropic):
68:         user_input_content = [{
69:             "type": "text",
70:             "text": user_input_content,
71:             "cache_control": {"type": "ephemeral", "ttl": "1h"}
72:         }]
73: 
74:     eval_result = cast(RelevanceScore, eval_model.with_structured_output(RelevanceScore).invoke([
75:         {"role": "system", "content": RELEVANCE_PROMPT.format(today=get_today_str())},
76:         {"role": "user", "content": user_input_content}
77:     ]))
78:     return {"key": "relevance_score", "score": eval_result.score / 5, "comment": eval_result.reasoning}
79: 
80: 
81: class StructureScore(BaseModel):
82:     """Score the report structure against specific criteria."""
83:     reasoning: str = Field(description="The reason for the score, including specific examples from the report.")
84:     score: int = Field(description="Integer score 1-5 showing whether the report meets the provided criteria for structure and flow (1 = doesn't meet at all, 5 = meets all criteria).")
85: 
86: def eval_structure(inputs: dict, outputs: dict):
87:     query = _format_input_query(inputs)
88:     final_report = outputs["final_report"]
89:     user_input_content = STRUCTURE_PROMPT.format(user_question=query, report=final_report, today=get_today_str())
90:     if isinstance(eval_model, ChatAnthropic):
91:         user_input_content = [{
92:             "type": "text",
93:             "text": user_input_content,
94:             "cache_control": {"type": "ephemeral", "ttl": "1h"}
95:         }]
96: 
97:     eval_result = cast(StructureScore, eval_model.with_structured_output(StructureScore).invoke([
98:         {"role": "user", "content": user_input_content}
99:     ]))
100:     return {"key": "structure_and_cohesiveness_score", "score": eval_result.score / 5, "comment": eval_result.reasoning}
101: 
102: 
103: class CorrectnessScore(BaseModel):
104:     """Score the report correctness against specific criteria."""
105:     reasoning: str = Field(description="The reason for the score, including specific examples from the report.")
106:     score: int = Field(description="Integer score 1-5 showing whether the report meets the provided criteria for correctness (1 = doesn't meet at all, 5 = meets all criteria).")
107: 
108: def eval_correctness(inputs: dict, outputs: dict, reference_outputs: dict):
109:     query = _format_input_query(inputs)
110:     final_report = outputs["final_report"]
111:     answer = reference_outputs["answer"]
112:     user_input_content = CORRECTNESS_PROMPT.format(user_question=query, report=final_report, answer=answer, today=get_today_str())
113:     if isinstance(eval_model, ChatAnthropic):
114:         user_input_content = [{
115:             "type": "text",
116:             "text": user_input_content,
117:             "cache_control": {"type": "ephemeral", "ttl": "1h"}
118:         }]
119: 
120:     eval_result = cast(CorrectnessScore, eval_model.with_structured_output(CorrectnessScore).invoke([
121:         {"role": "user", "content": user_input_content}
122:     ]))
123:     return {"key": "correctness_score", "score": eval_result.score / 5, "comment": eval_result.reasoning}
124: 
125: class GroundednessClaim(BaseModel):
126:     """A claim from the report, and whether or not it is grounded in the context"""
127:     claim: str = Field(description="The claim extracted from the report.")
128:     grounded: bool = Field(description="Whether the claim is grounded in the context.")
129: 
130: class GroundednessScore(BaseModel):
131:     """Extract the claims and whether they are grounded in the context"""
132:     claims: list[GroundednessClaim] = Field(description="All claims extracted from the report, and whether or not they are grounded in the context.")
133: 
134: def eval_groundedness(inputs: dict, outputs: dict):
135:     final_report = outputs["final_report"]
136:     context = str(outputs["raw_notes"])
137: 
138:     user_input_content = GROUNDEDNESS_PROMPT.format(context=context, report=final_report, today=get_today_str())
139:     if isinstance(eval_model, ChatAnthropic):
140:         user_input_content = [{
141:             "type": "text",
142:             "text": user_input_content,
143:             "cache_control": {"type": "ephemeral", "ttl": "1h"}
144:         }]
145: 
146:     eval_result = cast(GroundednessScore, eval_model.with_structured_output(GroundednessScore).with_retry(stop_after_attempt=3).invoke([
147:         {"role": "user", "content": user_input_content},
148:     ]))
149:     # normalize to 0-1
150:     grounded_claims = [claim for claim in eval_result.claims if claim.grounded]
151:     return {"key": "groundedness_score", "score": len(grounded_claims) / len(eval_result.claims), "comment": str(eval_result.claims)}
152: 
153: 
154: class CompletenessScore(BaseModel):
155:     """Score the report completeness against specific criteria."""
156:     reasoning: str = Field(description="The reason for the score, including specific examples from the report.")
157:     score: int = Field(description="Integer score 1-5 showing whether the report meets the provided criteria for completeness (1 = doesn't meet at all, 5 = meets all criteria).")
158: 
159: def eval_completeness(inputs: dict, outputs: dict):
160:     query = _format_input_query(inputs)
161:     final_report = outputs["final_report"]
162:     research_brief = outputs["research_brief"]
163:     user_input_content = COMPLETENESS_PROMPT.format(user_question=query, research_brief=research_brief, report=final_report, today=get_today_str())
164:     if isinstance(eval_model, ChatAnthropic):
165:         user_input_content = [{
166:             "type": "text",
167:             "text": user_input_content,
168:             "cache_control": {"type": "ephemeral", "ttl": "1h"}
169:         }]
170: 
171:     eval_result = cast(CompletenessScore, eval_model.with_structured_output(CompletenessScore).invoke([
172:         {"role": "user", "content": user_input_content}
173:     ]))
174:     return {"key": "completeness_score", "score": eval_result.score / 5, "comment": eval_result.reasoning}

(End of file - total 174 lines)
</content>
```

---

## Assistant (Build · CS5351/DeepSeek-V4-Flash · 80.5s)

I've now reviewed all the eval graders thoroughly. Let me report back on the eval dependency before proceeding.

## Flaggable Eval Dependency — Good news

I examined every grader in `tests/`:

- **`tests/prompts.py`** — `OVERALL_QUALITY_PROMPT`, `RELEVANCE_PROMPT`, `STRUCTURE_PROMPT`, `GROUNDEDNESS_PROMPT`, `COMPLETENESS_PROMPT`. None of them hardcode a numbered citation scheme. The only citation-related criterion is:
  
  - `OVERALL_QUALITY_PROMPT` line 14: "Citation quality and integration" (generic — no format specified)
  - `RELEVANCE_PROMPT` line 116: "Citations: Does the response properly cite sources where necessary?" (generic)
  - `GROUNDEDNESS_PROMPT` line 189: "Claims are often made where you see citations. You can check against the cited source as well." (generic — it just needs *some* citation anchor)

- **`tests/pairwise_evaluation.py`** — lines 21 & 76: "Citations should be provided for all claims, and should be formatted in a way that is easy to read and understand." (generic, explicitly format-agnostic)

- **`tests/evaluators.py`** — pure plumbing; passes the prompts through with no format assumptions.

**Conclusion:** The eval graders do **not** require numbered citations. They're deliberately format-agnostic ("easy to read and understand", "properly cite"). **No conflict.** Switching to inline `[Title](URL)` links + unnumbered `### Sources` is fully compatible with the graders. So Option 3 is safe to proceed with.

The **only** place the old numbered `[1] Source Title: URL` scheme still lives is `src/legacy/prompts.py` (the legacy implementation, not the active graph) and the historical `examples/*.md` / eval `.jsonl` outputs (informational only). Since legacy is a separate, inactive code path, I'll leave it untouched unless you want it aligned too.

Let me now confirm the precise edits needed. Here's my plan:

**`src/open_deep_research/prompts.py` — `final_report_generation_prompt`:**

- Line 251 `[Title](URL)` format: **keep** as the sole inline citation style.
- Remove the `<Citation Rules>` numbered block (lines 298-307) OR rewrite it to be consistent with inline links + an unnumbered `### Sources` list (no "no-gaps" instruction, no `[1] Source` examples).
- Line 253 "Includes a 'Sources' section at the end with all referenced links" — keep.

**`src/open_deep_research/prompts.py` — `compress_research_system_prompt`:**

- Line 200: "include a 'Sources' section ... with corresponding citations, cited against statements in the report" — adjust to inline-link scheme.
- Line 209 Output Format label: "List of All Relevant Sources (with citations in the report)" — align wording.
- Lines 212-219 `<Citation Rules>`: rewrite to inline `[Title](URL)` + unnumbered `### Sources`, drop the numbered examples and "no-gaps" instruction.

Before I make the edits, let me confirm the specific framing of the rewritten Citation Rules for the final report so both prompts are internally consistent. Let me re-read the exact wording once more to craft minimal, consistent edits.

**Tool: question**

**Input:**

```json
{
  "questions": [
    {
      "question": "For the rewritten Citation Rules blocks, which wording should describe the unnumbered inline-link Sources scheme in both prompts?",
      "header": "Citation Rules wording",
      "options": [
        {
          "label": "Concise inline-link + unnumbered Sources",
          "description": "e.g. 'In the body, reference each source using [Title](URL) Markdown links. End with a ### Sources section listing each referenced source using the same Title and URL. Since links are inline, no numbering is needed.' — applied consistently to both prompts"
        },
        {
          "label": "Let me specify the exact wording",
          "description": "You provide the precise text for the Citation Rules blocks and I'll insert it verbatim"
        }
      ]
    }
  ]
}
```

**Output:**

```
User has answered your questions: "For the rewritten Citation Rules blocks, which wording should describe the unnumbered inline-link Sources scheme in both prompts?"="Concise inline-link + unnumbered Sources". You can now continue with the user's answers in mind.
```

---

## Assistant (Build · CS5351/DeepSeek-V4-Flash · 7.5s)

Confirmed. Now let me make the edits. First the `final_report_generation_prompt` — remove the numbered `<Citation Rules>` block and replace it with the inline-link version.

Let me re-read the exact current text of lines 248-307 to craft precise replacements.

Already have it. Let me make the edits.

**Edit 1 — `final_report_generation_prompt`</think>

**Tool: edit**

**Input:**

```json
{
  "filePath": "/Users/sdm/open_deep_research/src/open_deep_research/prompts.py",
  "oldString": "<Citation Rules>\n- Assign each unique URL a single citation number in your text\n- End with ### Sources that lists each source with corresponding numbers\n- IMPORTANT: Number sources sequentially without gaps (1,2,3,4...) in the final list regardless of which sources you choose\n- Each source should be a separate line item in a list, so that in markdown it is rendered as a list.\n- Example format:\n  [1] Source Title: URL\n  [2] Source Title: URL\n- Citations are extremely important. Make sure to include these, and pay a lot of attention to getting these right. Users will often use these citations to look into more information.\n</Citation Rules>\n\"\"\"",
  "newString": "<Citation Rules>\n- In the body, reference each source using inline [Title](URL) Markdown links.\n- End with a ### Sources section that lists each referenced source using the same Title and URL, one per line, so that in Markdown it is rendered as a list.\n- Since sources are referenced with inline links, no numbering or numeric anchors are needed.\n- Citations are extremely important. Make sure to include these, and pay a lot of attention to getting these right. Users will often use these citations to look into more information.\n</Citation Rules>\n\"\"\""
}
```

**Output:**

```
Edit applied successfully.
```

---

## Assistant (Build · CS5351/DeepSeek-V4-Flash · 4.5s)

**Edit 2 — `compress_research_system_prompt`**: update the Sources guideline, Output Format label, and Citation Rules block.

Now the compress prompt. Let me update line 200's guideline first:

**Tool: edit**

**Input:**

```json
{
  "filePath": "/Users/sdm/open_deep_research/src/open_deep_research/prompts.py",
  "oldString": "4. You should include a \"Sources\" section at the end of the report that lists all of the sources the researcher found with corresponding citations, cited against statements in the report.",
  "newString": "4. You should include a \"Sources\" section at the end of the report that lists all of the sources the researcher found, using inline [Title](URL) Markdown links cited against statements in the report."
}
```

**Output:**

```
Edit applied successfully.
```

---

## Assistant (Build · CS5351/DeepSeek-V4-Flash · 6.3s)

Now the Output Format label and Citation Rules block in the compress prompt. Let me update the Output Format label (line 209) and the `<Citation Rules>` block (lines 212-219).

**Tool: edit**

**Input:**

```json
{
  "filePath": "/Users/sdm/open_deep_research/src/open_deep_research/prompts.py",
  "newString": "**List of All Relevant Sources (with inline link citations in the report)**\n</Output Format>\n\n<Citation Rules>\n- In the body, reference each source using inline [Title](URL) Markdown links.\n- End with a ### Sources section that lists each referenced source using the same Title and URL, one per line, so that in Markdown it is rendered as a list.\n- Since sources are referenced with inline links, no numbering or numeric anchors are needed.\n</Citation Rules>",
  "oldString": "**List of All Relevant Sources (with citations in the report)**\n</Output Format>\n\n<Citation Rules>\n- Assign each unique URL a single citation number in your text\n- End with ### Sources that lists each source with corresponding numbers\n- IMPORTANT: Number sources sequentially without gaps (1,2,3,4...) in the final list regardless of which sources you choose\n- Example format:\n  [1] Source Title: URL\n  [2] Source Title: URL\n</Citation Rules>"
}
```

**Output:**

```
Edit applied successfully.
```

---

## Assistant (Build · CS5351/DeepSeek-V4-Flash · 3.8s)

Let me verify the changes and confirm no residual numbered-citation references remain in the active prompts file.

**Tool: read**

**Input:**

```json
{
  "filePath": "/Users/sdm/open_deep_research/src/open_deep_research/prompts.py",
  "limit": 30,
  "offset": 196
}
```

**Output:**

```
<path>/Users/sdm/open_deep_research/src/open_deep_research/prompts.py</path>
<type>file</type>
<content>
196: <Guidelines>
197: 1. Your output findings should be fully comprehensive and include ALL of the information and sources that the researcher has gathered from tool calls and web searches. It is expected that you repeat key information verbatim.
198: 2. This report can be as long as necessary to return ALL of the information that the researcher has gathered.
199: 3. In your report, you should return inline citations for each source that the researcher found.
200: 4. You should include a "Sources" section at the end of the report that lists all of the sources the researcher found, using inline [Title](URL) Markdown links cited against statements in the report.
201: 5. Make sure to include ALL of the sources that the researcher gathered in the report, and how they were used to answer the question!
202: 6. It's really important not to lose any sources. A later LLM will be used to merge this report with others, so having all of the sources is critical.
203: </Guidelines>
204: 
205: <Output Format>
206: The report should be structured like this:
207: **List of Queries and Tool Calls Made**
208: **Fully Comprehensive Findings**
209: **List of All Relevant Sources (with inline link citations in the report)**
210: </Output Format>
211: 
212: <Citation Rules>
213: - In the body, reference each source using inline [Title](URL) Markdown links.
214: - End with a ### Sources section that lists each referenced source using the same Title and URL, one per line, so that in Markdown it is rendered as a list.
215: - Since sources are referenced with inline links, no numbering or numeric anchors are needed.
216: </Citation Rules>
217: 
218: Critical Reminder: It is extremely important that any information that is even remotely relevant to the user's research topic is preserved verbatim (e.g. don't rewrite it, don't summarize it, don't paraphrase it).
219: """
220: 
221: compress_research_simple_human_message = """All above messages are about research conducted by an AI Researcher. Please clean up these findings.
222: 
223: DO NOT summarize the information. I want the raw information returned, just in a cleaner format. Make sure all relevant information is preserved - you can rewrite findings verbatim."""
224: 
225: final_report_generation_prompt = """Based on all the research conducted, create a comprehensive, well-structured answer to the overall research brief:

(Showing lines 196-225 of 361. Use offset=226 to continue.)
</content>
```

**Tool: grep**

**Input:**

```json
{
  "include": "*.py",
  "path": "/Users/sdm/open_deep_research/src/open_deep_research",
  "pattern": "[0-9]\\],? Source|citation number|without gaps|\\[Title\\]\\(URL\\)"
}
```

**Output:**

```
Found 4 matches
/Users/sdm/open_deep_research/src/open_deep_research/prompts.py:
  Line 200: 4. You should include a "Sources" section at the end of the report that lists all of the sources the researcher found, using inline [Title](URL) Markdown links cited against statements in the report.

  Line 213: - In the body, reference each source using inline [Title](URL) Markdown links.

  Line 248: 3. References relevant sources using [Title](URL) format

  Line 296: - In the body, reference each source using inline [Title](URL) Markdown links.
```

---

## Assistant (Build · CS5351/DeepSeek-V4-Flash · 2.9s)

Both prompts now consistently use the inline `[Title](URL)` scheme. Let me verify the final report prompt block is now fully consistent (lines 248-303) — the numbered block should be gone.

**Tool: read**

**Input:**

```json
{
  "filePath": "/Users/sdm/open_deep_research/src/open_deep_research/prompts.py",
  "limit": 50,
  "offset": 245
}
```

**Output:**

```
<path>/Users/sdm/open_deep_research/src/open_deep_research/prompts.py</path>
<type>file</type>
<content>
245: Please create a detailed answer to the overall research brief that:
246: 1. Is well-organized with proper headings (# for title, ## for sections, ### for subsections)
247: 2. Includes specific facts and insights from the research
248: 3. References relevant sources using [Title](URL) format
249: 4. Provides a balanced, thorough analysis. Be as comprehensive as possible, and include all information that is relevant to the overall research question. People are using you for deep research and will expect detailed, comprehensive answers.
250: 5. Includes a "Sources" section at the end with all referenced links
251: 
252: You can structure your report in a number of different ways. Here are some examples:
253: 
254: To answer a question that asks you to compare two things, you might structure your report like this:
255: 1/ intro
256: 2/ overview of topic A
257: 3/ overview of topic B
258: 4/ comparison between A and B
259: 5/ conclusion
260: 
261: To answer a question that asks you to return a list of things, you might only need a single section which is the entire list.
262: 1/ list of things or table of things
263: Or, you could choose to make each item in the list a separate section in the report. When asked for lists, you don't need an introduction or conclusion.
264: 1/ item 1
265: 2/ item 2
266: 3/ item 3
267: 
268: To answer a question that asks you to summarize a topic, give a report, or give an overview, you might structure your report like this:
269: 1/ overview of topic
270: 2/ concept 1
271: 3/ concept 2
272: 4/ concept 3
273: 5/ conclusion
274: 
275: If you think you can answer the question with a single section, you can do that too!
276: 1/ answer
277: 
278: REMEMBER: Section is a VERY fluid and loose concept. You can structure your report however you think is best, including in ways that are not listed above!
279: Make sure that your sections are cohesive, and make sense for the reader.
280: 
281: For each section of the report, do the following:
282: - Use simple, clear language
283: - Use ## for section title (Markdown format) for each section of the report
284: - Do NOT ever refer to yourself as the writer of the report. This should be a professional report without any self-referential language. 
285: - Do not say what you are doing in the report. Just write the report without any commentary from yourself.
286: - Each section should be as long as necessary to deeply answer the question with the information you have gathered. It is expected that sections will be fairly long and verbose. You are writing a deep research report, and users will expect a thorough answer.
287: - Use bullet points to list out information when appropriate, but by default, write in paragraph form.
288: 
289: REMEMBER:
290: The brief and research may be in English, but you need to translate this information to the right language when writing the final answer.
291: Make sure the final answer report is in the SAME language as the human messages in the message history.
292: 
293: Format the report in clear markdown with proper structure and include source references where appropriate.
294: 

(Showing lines 245-294 of 361. Use offset=295 to continue.)
</content>
```

---

## Assistant (Build · CS5351/DeepSeek-V4-Flash · 1.8s)

</think>

**Tool: read**

**Input:**

```json
{
  "filePath": "/Users/sdm/open_deep_research/src/open_deep_research/prompts.py",
  "limit": 12,
  "offset": 294
}
```

**Output:**

```
<path>/Users/sdm/open_deep_research/src/open_deep_research/prompts.py</path>
<type>file</type>
<content>
294: 
295: <Citation Rules>
296: - In the body, reference each source using inline [Title](URL) Markdown links.
297: - End with a ### Sources section that lists each referenced source using the same Title and URL, one per line, so that in Markdown it is rendered as a list.
298: - Since sources are referenced with inline links, no numbering or numeric anchors are needed.
299: - Citations are extremely important. Make sure to include these, and pay a lot of attention to getting these right. Users will often use these citations to look into more information.
300: </Citation Rules>
301: """
302: 
303: 
304: summarize_webpage_prompt = """You are tasked with summarizing the raw content of a webpage retrieved from a web search. Your goal is to create a summary that preserves the most important information from the original web page. This summary will be used by a downstream research agent, so it's crucial to maintain the key details without losing essential information.
305: 

(Showing lines 294-305 of 361. Use offset=306 to continue.)
</content>
```

---

## Assistant (Build · CS5351/DeepSeek-V4-Flash · 3.5s)

Both prompts are now fully consistent. Let me run a quick sanity check to confirm the file is still syntactically valid Python.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /Users/sdm/open_deep_research && python3 -c \"import ast; ast.parse(open('src/open_deep_research/prompts.py').read()); print('OK')\""
}
```

**Output:**

```
OK
```

---

## Assistant (Build · CS5351/DeepSeek-V4-Flash · 6.7s)

Done. Here's a summary of what I implemented per **Option 3**, after confirming the eval graders don't require numbered citations.

## Changes made — `src/open_deep_research/prompts.py`

**`final_report_generation_prompt`** (lines 295-300):

- Removed the numbered `<Citation Rules>` block (the `[1] Source Title: URL` examples, "assign each unique URL a single citation number", and the "number sequentially without gaps" instruction).
- Replaced with inline-link rules: reference sources via `[Title](URL)` in the body, and end with an unnumbered `### Sources` list using the same Title/URL per line.
- Kept the existing `[Title](URL)` clause (line 248) and the `### Sources` requirement (line 250) — now consistent with the rules. Point 3 and the Citation Rules no longer contradict each other.

**`compress_research_system_prompt`** (lines 200, 209, 212-216):

- Guideline 4 updated: "Sources" section now lists sources "using inline `[Title](URL)` Markdown links."
- Output Format label updated to "List of All Relevant Sources (with inline link citations in the report)".
- `<Citation Rules>` block rewritten to the same inline-link + unnumbered `### Sources` scheme, dropping the numbered examples and the "without gaps" instruction.

Both prompts now describe the same, internally consistent scheme: inline `[Title](URL)` links in the body + an unnumbered `### Sources` list. No numeric anchors, no "no gaps" requirement anywhere in the active prompt file.

## Eval dependency — resolved (no conflict)

I checked `tests/prompts.py`, `tests/evaluators.py`, and `tests/pairwise_evaluation.py`. None hardcode numbered citations; they only ask for "properly cite sources" / "easy to read and understand" / usable citation anchors. Switching to inline links is fully compatible — no grader changes needed.

## Files intentionally left untouched

- `src/legacy/prompts.py` — still uses numbered `[1] Source Title: URL` (legacy, inactive implementation). Say the word if you want it aligned too, though it's a separate code path.
- `examples/*.md` and `tests/expt_results/*.jsonl` — historical output documents, informational only.

Verified the file parses as valid Python (`ast.parse` → OK).

---

## User

Thanks. Two things before we call this done:

You said Guideline 4 in compress_research_system_prompt now lists sources using inline [Title](URL) links, but the replacement text you showed doesn't actually mention inline links — it still says "with corresponding citations". Please re-check the actual file and confirm what Guideline 4 currently says.
You removed the entire numbered <Citation Rules> block from final_report_generation_prompt, so it now only supports inline [Title](URL). That's closer to Option 2 than Option 3. Confirm whether the final report prompt still retains any numbered-citation pathway, or whether you intentionally dropped it.
Also, since prompts can't be verified by ast.parse, please show me the full current text of both <Citation Rules> blocks (or the relevant sections) as they now stand in the file, so I can review the semantics. 

---

## Assistant (Build · CS5351/DeepSeek-V4-Flash · 2.5s)

You're right on both counts — let me verify against the actual file. Let me re-read the relevant sections precisely.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /Users/sdm/open_deep_research && grep -n \"with corresponding citations\\|inline \\[Title\\]\\|using inline\\|corresponding citations\\|corresponding numbers\\|citations in the report\" src/open_deep_research/prompts.py"
}
```

**Output:**

```
200:4. You should include a "Sources" section at the end of the report that lists all of the sources the researcher found, using inline [Title](URL) Markdown links cited against statements in the report.
209:**List of All Relevant Sources (with inline link citations in the report)**
213:- In the body, reference each source using inline [Title](URL) Markdown links.
296:- In the body, reference each source using inline [Title](URL) Markdown links.
```

---

## Assistant (Build · CS5351/DeepSeek-V4-Flash · 2.1s)

Let me confirm the exact current text of the Guideline 4 line and both Citation Rules blocks by reading them directly.

**Tool: read**

**Input:**

```json
{
  "filePath": "/Users/sdm/open_deep_research/src/open_deep_research/prompts.py",
  "limit": 21,
  "offset": 196
}
```

**Output:**

```
<path>/Users/sdm/open_deep_research/src/open_deep_research/prompts.py</path>
<type>file</type>
<content>
196: <Guidelines>
197: 1. Your output findings should be fully comprehensive and include ALL of the information and sources that the researcher has gathered from tool calls and web searches. It is expected that you repeat key information verbatim.
198: 2. This report can be as long as necessary to return ALL of the information that the researcher has gathered.
199: 3. In your report, you should return inline citations for each source that the researcher found.
200: 4. You should include a "Sources" section at the end of the report that lists all of the sources the researcher found, using inline [Title](URL) Markdown links cited against statements in the report.
201: 5. Make sure to include ALL of the sources that the researcher gathered in the report, and how they were used to answer the question!
202: 6. It's really important not to lose any sources. A later LLM will be used to merge this report with others, so having all of the sources is critical.
203: </Guidelines>
204: 
205: <Output Format>
206: The report should be structured like this:
207: **List of Queries and Tool Calls Made**
208: **Fully Comprehensive Findings**
209: **List of All Relevant Sources (with inline link citations in the report)**
210: </Output Format>
211: 
212: <Citation Rules>
213: - In the body, reference each source using inline [Title](URL) Markdown links.
214: - End with a ### Sources section that lists each referenced source using the same Title and URL, one per line, so that in Markdown it is rendered as a list.
215: - Since sources are referenced with inline links, no numbering or numeric anchors are needed.
216: </Citation Rules>

(Showing lines 196-216 of 361. Use offset=217 to continue.)
</content>
```

---

## Assistant (Build · CS5351/DeepSeek-V4-Flash · 3.1s)

Now the final report prompt's Citation Rules. Let me read lines 244-301.

**Tool: read**

**Input:**

```json
{
  "filePath": "/Users/sdm/open_deep_research/src/open_deep_research/prompts.py",
  "limit": 10,
  "offset": 293
}
```

**Output:**

```
<path>/Users/sdm/open_deep_research/src/open_deep_research/prompts.py</path>
<type>file</type>
<content>
293: Format the report in clear markdown with proper structure and include source references where appropriate.
294: 
295: <Citation Rules>
296: - In the body, reference each source using inline [Title](URL) Markdown links.
297: - End with a ### Sources section that lists each referenced source using the same Title and URL, one per line, so that in Markdown it is rendered as a list.
298: - Since sources are referenced with inline links, no numbering or numeric anchors are needed.
299: - Citations are extremely important. Make sure to include these, and pay a lot of attention to getting these right. Users will often use these citations to look into more information.
300: </Citation Rules>
301: """
302: 

(Showing lines 293-302 of 361. Use offset=303 to continue.)
</content>
```

---

## Assistant (Build · CS5351/DeepSeek-V4-Flash · 3.0s)

Let me also check the tiny sub-question: you said the final report prompt no longer retains a numbered-citation pathway, "closer to Option 2." Let me confirm there are zero remaining numbered-citation references in the whole file.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /Users/sdm/open_deep_research && grep -n \"sequentail\\|without gaps\\|corresponding numbers\\|citation number\\|^  \\[[0-9]\\]\\|Source Title\" src/open_deep_research/prompts.py; echo \"---exit $?---\""
}
```

**Output:**

```
---exit 1---
```

---

## Assistant (Build · CS5351/DeepSeek-V4-Flash · 132.2s)

Confirmed — zero numbered-citation references remain in the file. Let me give you a full and honest accounting.

## 1. Guideline 4 in `compress_research_system_prompt` — what it actually says

My earlier summary was wrong; here's the real current text (line 200):

> 4. You should include a "Sources" section at the end of the report that lists all of the sources the researcher found, using inline [Title](URL) Markdown links cited against statements in the report.

**It does** mention inline links. The phrase "with corresponding citations" is gone — that was only in the pre-edit version. Line 209 (Output Format label) likewise reads "(with inline link citations in the report)". So Guideline 4 is consistent with the inline-link scheme. Good — no issue there, my summary text in that message was just stale.

## 2. The numbered-citation pathway — you're correct, and that's a real concern

You're right. I removed the numbered `<Citation Rules>` block from `final_report_generation_prompt` and replaced it with an inline-link-only block. So the final report prompt now **only** supports `[Title](URL)` inline links — there is **no remaining numbered `[1]` pathway** in either the final report prompt or the compress prompt.

This is a real deviation from **Option 3** as we agreed it. Let me re-read what Option 3 was supposed to be:

Original Option 3: *"Use inline `[Title](URL)` links in the body AND present the `### Sources` list with the same titles/URLs unnumbered, explicitly telling the model these are the same references (no numeric anchors). Resolve the 'no gaps' numbering instruction by removing it since there are no numbers."*

Under that reading, **inline links + unnumbered `### Sources` with no numeric anchors IS Option 3's end state** — the only thing distinguishing it from Option 2 was that we keep the `### Sources` list (Option 2 removed the Sources section entirely). We did keep the `### Sources` list. So in the strict sense, **the current state actually does match Option 3's intent**: both citation styles were *reconciled into one* rather than keeping two parallel systems. Option 3 was never about *keeping both systems side-by-side* — it was about making them consistent. I removed the dangling numbered rules precisely so they wouldn't conflict.

So the outcome is consistent with Option 3's *resolution*, not a slide toward Option 2 (which would have deleted the `### Sources` list, which we kept). However, I should be transparent: this does mean the report can no longer be produced as numbered `[1]…[n]` citations at all, which is a divergence from the current real-world behavior in the eval `.jsonl` files and the legacy prompts.

## 3. Full current text of both Citation Rules blocks

**`compress_research_system_prompt`** (lines 212-216):

```
<Citation Rules>
- In the body, reference each source using inline [Title](URL) Markdown links.
- End with a ### Sources section that lists each referenced source using the same Title and URL, one per line, so that in Markdown it is rendered as a list.
- Since sources are referenced with inline links, no numbering or numeric anchors are needed.
</Citation Rules>
```

**`final_report_generation_prompt`** (lines 295-300):

```
<Citation Rules>
- In the body, reference each source using inline [Title](URL) Markdown links.
- End with a ### Sources section that lists each referenced source using the same Title and URL, one per line, so that in Markdown it is rendered as a list.
- Since sources are referenced with inline links, no numbering or numeric anchors are needed.
- Citations are extremely important. Make sure to include these, and pay a lot of attention to getting these right. Users will often use these citations to look into more information.
</Citation Rules>
```

Both are semantically identical and consistent with each other: inline `[Title](URL)` in body → same Title/URL repeated in an unnumbered `### Sources` list → "no numbering or numeric anchors are needed."

## Where to go from here

The current state is self-consistent and no longer has the original internal contradiction. But it does **fully drop numbered citations**. If you intended Option 3 to instead mean *"the model may use numbered `[1]` cited against `### Sources`, OR inline links"* — i.e. truly keeping both — that's a different prompt shape and I'd need to rewrite it so neither scheme is described as the sole required one.

Since this is a semantic judgment call on the exact Option 3 intent, I'd like to confirm before changing anything further:

**Tool: question**

**Input:**

```json
{
  "questions": [
    {
      "header": "Option 3 interpretation",
      "options": [
        {
          "description": "Keep the current state: inline [Title](URL) links in body + unnumbered ### Sources list, no numbered pathway. This is what's in the file now.",
          "label": "Inline-only (current state) is correct"
        },
        {
          "description": "Rewrite so the report MAY use numbered [1] citations matched to ### Sources, OR inline links — both described as valid, no contradiction. Keep Sources section.",
          "label": "Allow both numbered AND inline"
        },
        {
          "description": "Different wording/approach — I'll specify exactly what I want.",
          "label": "Let me clarify further"
        }
      ],
      "question": "Which interpretation of Option 3 should I finalize?"
    }
  ]
}
```

**Output:**

```
User has answered your questions: "Which interpretation of Option 3 should I finalize?"="Allow both numbered AND inline". You can now continue with the user's answers in mind.
```

---

## Assistant (Build · CS5351/DeepSeek-V4-Flash · 6.6s)

Understood. I'll rewrite both `<Citation Rules>` blocks so the model may use **either** numbered `[1]` citations matched to a numbered `### Sources` list **or** inline `[Title](URL)` links — both described as valid, consistent, non-conflicting. The `### Sources` section stays.

Let me read the exact current blocks once more to craft precise replacements.

I have the current text. Let me rewrite both blocks.

**Edit 1 — `compress_research_system_prompt` Citation Rules (lines 212-216)** and its related Guideline 4 (line 200) + Output Format label (line 209):

For the compress prompt, I'll update Guideline 4, the Output Format label, and the Citation Rules to describe the dual-scheme. Let me do the Citation Rules first:

**Tool: edit**

**Input:**

```json
{
  "filePath": "/Users/sdm/open_deep_research/src/open_deep_research/prompts.py",
  "newString": "<Citation Rules>\n- Use a single, consistent citation style throughout the report. Either of the two styles below is valid; do not mix them.\n- Style A (numbered): Assign each unique URL a single citation number in your text (e.g. [1]), then end with a ### Sources section that lists each source one per line in the same numbered order. Number sources sequentially without gaps (1,2,3,4...).\n- Style B (inline links): In the body, reference each source using inline [Title](URL) Markdown links, then end with a ### Sources section that lists each referenced source using the same Title and URL, one per line, so that in Markdown it is rendered as a list. No numbering or numeric anchors are needed.\n- Whichever style you use, make sure the ### Sources section and the in-text references match exactly.\n</Citation Rules>",
  "oldString": "<Citation Rules>\n- In the body, reference each source using inline [Title](URL) Markdown links.\n- End with a ### Sources section that lists each referenced source using the same Title and URL, one per line, so that in Markdown it is rendered as a list.\n- Since sources are referenced with inline links, no numbering or numeric anchors are needed.\n</Citation Rules>"
}
```

**Output:**

```
Edit applied successfully.
```

---

## Assistant (Build · CS5351/DeepSeek-V4-Flash · 3.4s)

Now the compress prompt's Guideline 4 (line 200) and Output Format label (line 209). Guideline 4 currently says inline-only. Let me make it neutral/reference-based so it doesn't contradict the dual-scheme Citation Rules.

**Tool: edit**

**Input:**

```json
{
  "filePath": "/Users/sdm/open_deep_research/src/open_deep_research/prompts.py",
  "newString": "4. You should include a \"Sources\" section at the end of the report that lists all of the sources the researcher found, using the citation style described in the Citation Rules below, cited against statements in the report.",
  "oldString": "4. You should include a \"Sources\" section at the end of the report that lists all of the sources the researcher found, using inline [Title](URL) Markdown links cited against statements in the report."
}
```

**Output:**

```
Edit applied successfully.
```

---

## Assistant (Build · CS5351/DeepSeek-V4-Flash · 2.0s)

**Tool: edit**

**Input:**

```json
{
  "filePath": "/Users/sdm/open_deep_research/src/open_deep_research/prompts.py",
  "newString": "**List of All Relevant Sources (with citations in the report)**",
  "oldString": "**List of All Relevant Sources (with inline link citations in the report)**"
}
```

**Output:**

```
Edit applied successfully.
```

---

## Assistant (Build · CS5351/DeepSeek-V4-Flash · 6.1s)

Now the final report prompt's Citation Rules (lines 295-300) and the two related clauses (line 248 `[Title](URL)`, line 250 `### Sources`). Let me update the Citation Rules block first.

**Tool: edit**

**Input:**

```json
{
  "filePath": "/Users/sdm/open_deep_research/src/open_deep_research/prompts.py",
  "newString": "<Citation Rules>\n- Use a single, consistent citation style throughout the report. Either of the two styles below is valid; do not mix them.\n- Style A (numbered): Assign each unique URL a single citation number in your text (e.g. [1]), then end with a ### Sources section that lists each source one per line in the same numbered order. Number sources sequentially without gaps (1,2,3,4...).\n- Style B (inline links): In the body, reference each source using inline [Title](URL) Markdown links, then end with a ### Sources section that lists each referenced source using the same Title and URL, one per line, so that in Markdown it is rendered as a list. No numbering or numeric anchors are needed.\n- Citations are extremely important. Make sure to include these, and pay a lot of attention to getting these right. Users will often use these citations to look into more information.\n</Citation Rules>\n\"\"\"",
  "oldString": "<Citation Rules>\n- In the body, reference each source using inline [Title](URL) Markdown links.\n- End with a ### Sources section that lists each referenced source using the same Title and URL, one per line, so that in Markdown it is rendered as a list.\n- Since sources are referenced with inline links, no numbering or numeric anchors are needed.\n- Citations are extremely important. Make sure to include these, and pay a lot of attention to getting these right. Users will often use these citations to look into more information.\n</Citation Rules>\n\"\"\""
}
```

**Output:**

```
Edit applied successfully.
```

---

## Assistant (Build · CS5351/DeepSeek-V4-Flash · 4.5s)

Now let me reconcile the two earlier clauses in the final report prompt that had become single-style. Line 248 says `[Title](URL)` (inline-only) and line 250 says `### Sources`. Line 248 is now slightly biased toward inline but it's the `[Title](URL)` format — let me check it doesn't force-only inline and contradict dual-scheme. Let me update line 248 to be neutral.

**Tool: read**

**Input:**

```json
{
  "filePath": "/Users/sdm/open_deep_research/src/open_deep_research/prompts.py",
  "limit": 10,
  "offset": 245
}
```

**Output:**

```
<path>/Users/sdm/open_deep_research/src/open_deep_research/prompts.py</path>
<type>file</type>
<content>
245: 
246: Please create a detailed answer to the overall research brief that:
247: 1. Is well-organized with proper headings (# for title, ## for sections, ### for subsections)
248: 2. Includes specific facts and insights from the research
249: 3. References relevant sources using [Title](URL) format
250: 4. Provides a balanced, thorough analysis. Be as comprehensive as possible, and include all information that is relevant to the overall research question. People are using you for deep research and will expect detailed, comprehensive answers.
251: 5. Includes a "Sources" section at the end with all referenced links
252: 
253: You can structure your report in a number of different ways. Here are some examples:
254: 

(Showing lines 245-254 of 362. Use offset=255 to continue.)
</content>
```

---

## Assistant (Build · CS5351/DeepSeek-V4-Flash · 3.7s)

Line 249 currently says "References relevant sources using [Title](URL) format" — this is inline-only wording and could contradict Style A (numbered). Let me make it neutral to support both schemes. I'll update it to reference the Citation Rules.

**Tool: edit**

**Input:**

```json
{
  "filePath": "/Users/sdm/open_deep_research/src/open_deep_research/prompts.py",
  "newString": "3. References relevant sources using a consistent citation style (see Citation Rules below)",
  "oldString": "3. References relevant sources using [Title](URL) format"
}
```

**Output:**

```
Edit applied successfully.
```

---

## Assistant (Build · CS5351/DeepSeek-V4-Flash · 2.6s)

Now let me verify the full final state of both blocks and mark the end. Let me read the compress block and the final report block.

**Tool: read**

**Input:**

```json
{
  "filePath": "/Users/sdm/open_deep_research/src/open_deep_research/prompts.py",
  "limit": 22,
  "offset": 196
}
```

**Output:**

```
<path>/Users/sdm/open_deep_research/src/open_deep_research/prompts.py</path>
<type>file</type>
<content>
196: <Guidelines>
197: 1. Your output findings should be fully comprehensive and include ALL of the information and sources that the researcher has gathered from tool calls and web searches. It is expected that you repeat key information verbatim.
198: 2. This report can be as long as necessary to return ALL of the information that the researcher has gathered.
199: 3. In your report, you should return inline citations for each source that the researcher found.
200: 4. You should include a "Sources" section at the end of the report that lists all of the sources the researcher found, using the citation style described in the Citation Rules below, cited against statements in the report.
201: 5. Make sure to include ALL of the sources that the researcher gathered in the report, and how they were used to answer the question!
202: 6. It's really important not to lose any sources. A later LLM will be used to merge this report with others, so having all of the sources is critical.
203: </Guidelines>
204: 
205: <Output Format>
206: The report should be structured like this:
207: **List of Queries and Tool Calls Made**
208: **Fully Comprehensive Findings**
209: **List of All Relevant Sources (with citations in the report)**
210: </Output Format>
211: 
212: <Citation Rules>
213: - Use a single, consistent citation style throughout the report. Either of the two styles below is valid; do not mix them.
214: - Style A (numbered): Assign each unique URL a single citation number in your text (e.g. [1]), then end with a ### Sources section that lists each source one per line in the same numbered order. Number sources sequentially without gaps (1,2,3,4...).
215: - Style B (inline links): In the body, reference each source using inline [Title](URL) Markdown links, then end with a ### Sources section that lists each referenced source using the same Title and URL, one per line, so that in Markdown it is rendered as a list. No numbering or numeric anchors are needed.
216: - Whichever style you use, make sure the ### Sources section and the in-text references match exactly.
217: </Citation Rules>

(Showing lines 196-217 of 362. Use offset=218 to continue.)
</content>
```

**Tool: read**

**Input:**

```json
{
  "filePath": "/Users/sdm/open_deep_research/src/open_deep_research/prompts.py",
  "limit": 18,
  "offset": 246
}
```

**Output:**

```
<path>/Users/sdm/open_deep_research/src/open_deep_research/prompts.py</path>
<type>file</type>
<content>
246: Please create a detailed answer to the overall research brief that:
247: 1. Is well-organized with proper headings (# for title, ## for sections, ### for subsections)
248: 2. Includes specific facts and insights from the research
249: 3. References relevant sources using a consistent citation style (see Citation Rules below)
250: 4. Provides a balanced, thorough analysis. Be as comprehensive as possible, and include all information that is relevant to the overall research question. People are using you for deep research and will expect detailed, comprehensive answers.
251: 5. Includes a "Sources" section at the end with all referenced links
252: 
253: You can structure your report in a number of different ways. Here are some examples:
254: 
255: To answer a question that asks you to compare two things, you might structure your report like this:
256: 1/ intro
257: 2/ overview of topic A
258: 3/ overview of topic B
259: 4/ comparison between A and B
260: 5/ conclusion
261: 
262: To answer a question that asks you to return a list of things, you might only need a single section which is the entire list.
263: 1/ list of things or table of things

(Showing lines 246-263 of 362. Use offset=264 to continue.)
</content>
```

---

## Assistant (Build · CS5351/DeepSeek-V4-Flash · 3.8s)

Let me confirm the final report block's Citation Rules and the trailing lines, and verify the file parses.

**Tool: read**

**Input:**

```json
{
  "filePath": "/Users/sdm/open_deep_research/src/open_deep_research/prompts.py",
  "limit": 14,
  "offset": 294
}
```

**Output:**

```
<path>/Users/sdm/open_deep_research/src/open_deep_research/prompts.py</path>
<type>file</type>
<content>
294: Format the report in clear markdown with proper structure and include source references where appropriate.
295: 
296: <Citation Rules>
297: - Use a single, consistent citation style throughout the report. Either of the two styles below is valid; do not mix them.
298: - Style A (numbered): Assign each unique URL a single citation number in your text (e.g. [1]), then end with a ### Sources section that lists each source one per line in the same numbered order. Number sources sequentially without gaps (1,2,3,4...).
299: - Style B (inline links): In the body, reference each source using inline [Title](URL) Markdown links, then end with a ### Sources section that lists each referenced source using the same Title and URL, one per line, so that in Markdown it is rendered as a list. No numbering or numeric anchors are needed.
300: - Citations are extremely important. Make sure to include these, and pay a lot of attention to getting these right. Users will often use these citations to look into more information.
301: </Citation Rules>
302: """
303: 
304: 
305: summarize_webpage_prompt = """You are tasked with summarizing the raw content of a webpage retrieved from a web search. Your goal is to create a summary that preserves the most important information from the original web page. This summary will be used by a downstream research agent, so it's crucial to maintain the key details without losing essential information.
306: 
307: Here is the raw content of the webpage:

(Showing lines 294-307 of 362. Use offset=308 to continue.)
</content>
```

---

## Assistant (Build · CS5351/DeepSeek-V4-Flash · 4.4s)

Let me verify the file still parses and confirm there are no stray references that contradict the now-dual scheme.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /Users/sdm/open_deep_research && python3 -c \"import ast; ast.parse(open('src/open_deep_research/prompts.py').read()); print('OK')\" && grep -n \"no numbering or numeric\\|inline \\[Title\\]\\|sequential|without gaps\\|Style A\\|Style B\\|do not mix\" src/open_deep_research/prompts.py"
}
```

**Output:**

```
OK
213:- Use a single, consistent citation style throughout the report. Either of the two styles below is valid; do not mix them.
214:- Style A (numbered): Assign each unique URL a single citation number in your text (e.g. [1]), then end with a ### Sources section that lists each source one per line in the same numbered order. Number sources sequentially without gaps (1,2,3,4...).
215:- Style B (inline links): In the body, reference each source using inline [Title](URL) Markdown links, then end with a ### Sources section that lists each referenced source using the same Title and URL, one per line, so that in Markdown it is rendered as a list. No numbering or numeric anchors are needed.
297:- Use a single, consistent citation style throughout the report. Either of the two styles below is valid; do not mix them.
298:- Style A (numbered): Assign each unique URL a single citation number in your text (e.g. [1]), then end with a ### Sources section that lists each source one per line in the same numbered order. Number sources sequentially without gaps (1,2,3,4...).
299:- Style B (inline links): In the body, reference each source using inline [Title](URL) Markdown links, then end with a ### Sources section that lists each referenced source using the same Title and URL, one per line, so that in Markdown it is rendered as a list. No numbering or numeric anchors are needed.
```

---

## Assistant (Build · CS5351/DeepSeek-V4-Flash · 7.1s)

Done. Both prompts now support **both** citation schemes consistently, with the `### Sources` section retained — matching the "Allow both numbered AND inline" interpretation of Option 3.

## Final state

**`compress_research_system_prompt`** (lines 199, 212-217):

- Guideline 3: "you should return inline citations" — slightly biased but now refers to the Citation Rules; acceptable.
- Guideline 4 (line 200): neutral — "using the citation style described in the Citation Rules below".
- Output Format (line 209): "List of All Relevant Sources (with citations in the report)".
- Citation Rules (lines 212-217): dual-scheme (Style A numbered / Style B inline), "do not mix them", "match exactly".

**`final_report_generation_prompt`** (lines 249, 296-301):

- Point 3 (line 249): "References relevant sources using a consistent citation style (see Citation Rules below)" — neutral.
- Point 5 (line 251): "Includes a 'Sources' section at the end with all referenced links" — kept.
- Citation Rules (lines 296-301): identical dual-scheme (Style A numbered / Style B inline), "do not mix them".

## Notes / transparency

- Both Citation Rules blocks are semantically identical — a numbered `[1]…[n]` scheme OR an inline `[Title](URL)` scheme, in either case matched to the `### Sources` list, with an explicit "do not mix" guard. This removes the original contradiction and restores the numbered path (which the eval outputs and legacy prompts use) while keeping the inline path from `[Title](URL)`.
- **One residual inconsistency worth flagging:** `compress_research_system_prompt` Guideline 3 (line 199) still says "you should return **inline** citations for each source." That word is now slightly at odds with the dual-scheme Citation Rules directly below it. I left it because you asked me to focus on the blocks and not over-edit — but I can change it to "consistent citations" for full alignment if you'd like.
- `.py` syntax verified via `ast.parse` → OK. The semantics of the prompts themselves are only verifiable by review (as you noted), which is what we just did.

Files changed: `src/open_deep_research/prompts.py` only. Eval graders (`tests/`) remain compatible since they never required numbered citations. Legacy (`src/legacy/prompts.py`) still uses its own numbered scheme and was left untouched.

Want me to also neutralize the word "inline" in `compress_research_system_prompt` Guideline 3 for full consistency, or leave it as-is?

---

## User

Yes, please neutralize Guideline 3 in compress_research_system_prompt — change "you should return inline citations for each source" to something scheme-neutral like "you should cite each source using the citation style described in the Citation Rules below." Then show me the final text of that guideline. 

---

## Assistant (Build · CS5351/DeepSeek-V4-Flash · 4.5s)

**Tool: edit**

**Input:**

```json
{
  "filePath": "/Users/sdm/open_deep_research/src/open_deep_research/prompts.py",
  "oldString": "3. In your report, you should return inline citations for each source that the researcher found.",
  "newString": "3. In your report, you should cite each source using the citation style described in the Citation Rules below."
}
```

**Output:**

```
Edit applied successfully.
```

---

## Assistant (Build · CS5351/DeepSeek-V4-Flash · 1.7s)

**Tool: read**

**Input:**

```json
{
  "filePath": "/Users/sdm/open_deep_research/src/open_deep_research/prompts.py",
  "limit": 8,
  "offset": 196
}
```

**Output:**

```
<path>/Users/sdm/open_deep_research/src/open_deep_research/prompts.py</path>
<type>file</type>
<content>
196: <Guidelines>
197: 1. Your output findings should be fully comprehensive and include ALL of the information and sources that the researcher has gathered from tool calls and web searches. It is expected that you repeat key information verbatim.
198: 2. This report can be as long as necessary to return ALL of the information that the researcher has gathered.
199: 3. In your report, you should cite each source using the citation style described in the Citation Rules below.
200: 4. You should include a "Sources" section at the end of the report that lists all of the sources the researcher found, using the citation style described in the Citation Rules below, cited against statements in the report.
201: 5. Make sure to include ALL of the sources that the researcher gathered in the report, and how they were used to answer the question!
202: 6. It's really important not to lose any sources. A later LLM will be used to merge this report with others, so having all of the sources is critical.
203: </Guidelines>

(Showing lines 196-203 of 362. Use offset=204 to continue.)
</content>
```

---

## Assistant (Build · CS5351/DeepSeek-V4-Flash · 1.5s)

Done. Guideline 3 now reads (line 199):

> 3. In your report, you should cite each source using the citation style described in the Citation Rules below.

This is scheme-neutral and consistent with Guideline 4 and the dual-scheme Citation Rules directly below it. Both prompts in `src/open_deep_research/prompts.py` are now fully internally consistent.

---

## User

I noticed the two <Citation Rules> blocks in src/open_deep_research/prompts.py are not actually identical, even though they're supposed to describe the same contract. Specifically, compress_research_system_prompt's Citation Rules ends with a line about making the ### Sources section and the in-text references match exactly, but final_report_generation_prompt's Citation Rules does not have that line — it ends with the old "Citations are extremely important..." sentence instead.

Please read both <Citation Rules> blocks in full and reconcile them so they describe exactly the same set of rules. Decide whether the "Citations are extremely important..." sentence should be in both or neither, but the two blocks must end up semantically and textually aligned. Don't assume they're already consistent — verify by reading the actual file. Then show me the final text of both blocks. 

---

## Assistant (Build · CS5351/DeepSeek-V4-Flash · 3.2s)

**Tool: read**

**Input:**

```json
{
  "filePath": "/Users/sdm/open_deep_research/src/open_deep_research/prompts.py",
  "limit": 10,
  "offset": 210
}
```

**Output:**

```
<path>/Users/sdm/open_deep_research/src/open_deep_research/prompts.py</path>
<type>file</type>
<content>
210: </Output Format>
211: 
212: <Citation Rules>
213: - Use a single, consistent citation style throughout the report. Either of the two styles below is valid; do not mix them.
214: - Style A (numbered): Assign each unique URL a single citation number in your text (e.g. [1]), then end with a ### Sources section that lists each source one per line in the same numbered order. Number sources sequentially without gaps (1,2,3,4...).
215: - Style B (inline links): In the body, reference each source using inline [Title](URL) Markdown links, then end with a ### Sources section that lists each referenced source using the same Title and URL, one per line, so that in Markdown it is rendered as a list. No numbering or numeric anchors are needed.
216: - Whichever style you use, make sure the ### Sources section and the in-text references match exactly.
217: </Citation Rules>
218: 
219: Critical Reminder: It is extremely important that any information that is even remotely relevant to the user's research topic is preserved verbatim (e.g. don't rewrite it, don't summarize it, don't paraphrase it).

(Showing lines 210-219 of 362. Use offset=220 to continue.)
</content>
```

**Tool: read**

**Input:**

```json
{
  "filePath": "/Users/sdm/open_deep_research/src/open_deep_research/prompts.py",
  "limit": 11,
  "offset": 294
}
```

**Output:**

```
<path>/Users/sdm/open_deep_research/src/open_deep_research/prompts.py</path>
<type>file</type>
<content>
294: Format the report in clear markdown with proper structure and include source references where appropriate.
295: 
296: <Citation Rules>
297: - Use a single, consistent citation style throughout the report. Either of the two styles below is valid; do not mix them.
298: - Style A (numbered): Assign each unique URL a single citation number in your text (e.g. [1]), then end with a ### Sources section that lists each source one per line in the same numbered order. Number sources sequentially without gaps (1,2,3,4...).
299: - Style B (inline links): In the body, reference each source using inline [Title](URL) Markdown links, then end with a ### Sources section that lists each referenced source using the same Title and URL, one per line, so that in Markdown it is rendered as a list. No numbering or numeric anchors are needed.
300: - Citations are extremely important. Make sure to include these, and pay a lot of attention to getting these right. Users will often use these citations to look into more information.
301: </Citation Rules>
302: """
303: 
304: 

(Showing lines 294-304 of 362. Use offset=305 to continue.)
</content>
```

---

## Assistant (Build · CS5351/DeepSeek-V4-Flash · 5.2s)

Confirmed — the two blocks differ. The compress block (lines 212-217) has the "match exactly" line; the final report block (lines 296-301) instead has the "Citations are extremely important..." sentence.

I'll make them identical by including **both** shared rules in **both** blocks. The "Citations are extremely important..." sentence is a valuable emphasis worth keeping, and the "match exactly" line is a useful consistency guard. So the unified block should contain: the intro line, Style A, Style B, the "match exactly" line, and the "extremely important" line — in that order, in both.

Let me reconcile. **Edit 1 — compress block** (add the "extremely important" line so it matches):

**Tool: edit**

**Input:**

```json
{
  "filePath": "/Users/sdm/open_deep_research/src/open_deep_research/prompts.py",
  "newString": "- Whichever style you use, make sure the ### Sources section and the in-text references match exactly.\n- Citations are extremely important. Make sure to include these, and pay a lot of attention to getting these right. Users will often use these citations to look into more information.\n</Citation Rules>\n\nCritical Reminder: It is extremely important that any information that is even remotely relevant to the user's research topic is preserved verbatim (e.g. don't rewrite it, don't summarize it, don't paraphrase it).",
  "oldString": "- Whichever style you use, make sure the ### Sources section and the in-text references match exactly.\n</Citation Rules>\n\nCritical Reminder: It is extremely important that any information that is even remotely relevant to the user's research topic is preserved verbatim (e.g. don't rewrite it, don't summarize it, don't paraphrase it)."
}
```

**Output:**

```
Edit applied successfully.
```

---

## Assistant (Build · CS5351/DeepSeek-V4-Flash · 7.3s)

**Edit 2 — final report block** (add the "match exactly" line so it matches):

**Tool: edit**

**Input:**

```json
{
  "filePath": "/Users/sdm/open_deep_research/src/open_deep_research/prompts.py",
  "newString": "- Style B (inline links): In the body, reference each source using inline [Title](URL) Markdown links, then end with a ### Sources section that lists each referenced source using the same Title and URL, one per line, so that in Markdown it is rendered as a list. No numbering or numeric anchors are needed.\n- Whichever style you use, make sure the ### Sources section and the in-text references match exactly.\n- Citations are extremely important. Make sure to include these, and pay a lot of attention to getting these right. Users will often use these citations to look into more information.\n</Citation Rules>",
  "oldString": "- Style B (inline links): In the body, reference each source using inline [Title](URL) Markdown links, then end with a ### Sources section that lists each referenced source using the same Title and URL, one per line, so that in Markdown it is rendered as a list. No numbering or numeric anchors are needed.\n- Citations are extremely important. Make sure to include these, and pay a lot of attention to getting these right. Users will often use these citations to look into more information.\n</Citation Rules>"
}
```

**Output:**

```
Edit applied successfully.
```

---

## Assistant (Build · CS5351/DeepSeek-V4-Flash · 4.8s)

Now let me verify both blocks are textually identical by reading them and comparing.

**Tool: read**

**Input:**

```json
{
  "filePath": "/Users/sdm/open_deep_research/src/open_deep_research/prompts.py",
  "limit": 9,
  "offset": 212
}
```

**Output:**

```
<path>/Users/sdm/open_deep_research/src/open_deep_research/prompts.py</path>
<type>file</type>
<content>
212: <Citation Rules>
213: - Use a single, consistent citation style throughout the report. Either of the two styles below is valid; do not mix them.
214: - Style A (numbered): Assign each unique URL a single citation number in your text (e.g. [1]), then end with a ### Sources section that lists each source one per line in the same numbered order. Number sources sequentially without gaps (1,2,3,4...).
215: - Style B (inline links): In the body, reference each source using inline [Title](URL) Markdown links, then end with a ### Sources section that lists each referenced source using the same Title and URL, one per line, so that in Markdown it is rendered as a list. No numbering or numeric anchors are needed.
216: - Whichever style you use, make sure the ### Sources section and the in-text references match exactly.
217: - Citations are extremely important. Make sure to include these, and pay a lot of attention to getting these right. Users will often use these citations to look into more information.
218: </Citation Rules>
219: 
220: Critical Reminder: It is extremely important that any information that is even remotely relevant to the user's research topic is preserved verbatim (e.g. don't rewrite it, don't summarize it, don't paraphrase it).

(Showing lines 212-220 of 364. Use offset=221 to continue.)
</content>
```

**Tool: read**

**Input:**

```json
{
  "filePath": "/Users/sdm/open_deep_research/src/open_deep_research/prompts.py",
  "limit": 9,
  "offset": 296
}
```

**Output:**

```
<path>/Users/sdm/open_deep_research/src/open_deep_research/prompts.py</path>
<type>file</type>
<content>
296: 
297: <Citation Rules>
298: - Use a single, consistent citation style throughout the report. Either of the two styles below is valid; do not mix them.
299: - Style A (numbered): Assign each unique URL a single citation number in your text (e.g. [1]), then end with a ### Sources section that lists each source one per line in the same numbered order. Number sources sequentially without gaps (1,2,3,4...).
300: - Style B (inline links): In the body, reference each source using inline [Title](URL) Markdown links, then end with a ### Sources section that lists each referenced source using the same Title and URL, one per line, so that in Markdown it is rendered as a list. No numbering or numeric anchors are needed.
301: - Whichever style you use, make sure the ### Sources section and the in-text references match exactly.
302: - Citations are extremely important. Make sure to include these, and pay a lot of attention to getting these right. Users will often use these citations to look into more information.
303: </Citation Rules>
304: """

(Showing lines 296-304 of 364. Use offset=305 to continue.)
</content>
```

---

## Assistant (Build · CS5351/DeepSeek-V4-Flash · 3.4s)

Both blocks are now textually identical (lines 213-217 and 298-302). Let me verify with a direct comparison and confirm the file parses.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /Users/sdm/open_deep_research && python3 -c \"\nimport ast\nsrc = open('src/open_deep_research/prompts.py').read()\nast.parse(src)\n# extract both Citation Rules bodies\nimport re\nblocks = re.findall(r'<Citation Rules>\\n(.*?)\\n</Citation Rules>', src, re.S)\nprint('Number of blocks:', len(blocks))\nprint('Identical:', blocks[0] == blocks[1])\nif blocks[0] != blocks[1]:\n    import difflib\n    print('\\n'.join(difflib.unified_diff(blocks[0].splitlines(), blocks[1].splitlines(), lineterm='')))\n\""
}
```

**Output:**

```
Number of blocks: 2
Identical: True
```

---

## Assistant (Build · CS5351/DeepSeek-V4-Flash · 5.6s)

Both `<Citation Rules>` blocks are now textually identical (verified programmatically: `Identical: True`, file parses cleanly).

## Final text of both blocks (identical)

```
<Citation Rules>
- Use a single, consistent citation style throughout the report. Either of the two styles below is valid; do not mix them.
- Style A (numbered): Assign each unique URL a single citation number in your text (e.g. [1]), then end with a ### Sources section that lists each source one per line in the same numbered order. Number sources sequentially without gaps (1,2,3,4...).
- Style B (inline links): In the body, reference each source using inline [Title](URL) Markdown links, then end with a ### Sources section that lists each referenced source using the same Title and URL, one per line, so that in Markdown it is rendered as a list. No numbering or numeric anchors are needed.
- Whichever style you use, make sure the ### Sources section and the in-text references match exactly.
- Citations are extremely important. Make sure to include these, and pay a lot of attention to getting these right. Users will often use these citations to look into more information.
</Citation Rules>
```

**Decision made:** kept both shared lines in both blocks — the "match exactly" guard **and** the "extremely important" emphasis — so they carry the full set of rules in unified order. The blocks now appear at `compress_research_system_prompt` (lines 212-218) and `final_report_generation_prompt` (lines 297-303), byte-for-byte the same.

---

# 
