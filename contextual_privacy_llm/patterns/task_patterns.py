TASK_PATTERNS = {
    "Summarization": [
        r"summarize|summary|brief|overview",
        r"compress|condense|shorten",
        r"main points|key points|highlights",
        r"tldr|too long|cliff notes",
        r"recap|review|digest"
    ],
    
    "Prompt_Generation_For_AI_Models": [
        r"create prompt|generate prompt|write prompt",
        r"prompt engineering|prompt design",
        r"AI instruction|model instruction",
        r"optimize prompt|improve prompt",
        r"prompt for (GPT|AI|LLM|model)"
    ],
    
    "Story_And_Script_Generation": [
        r"write (story|script|narrative|plot)",
        r"create (story|script|scene|dialogue)",
        r"generate (story|plot|scene)",
        r"story about|write about",
        r"creative writing|fiction|narrative"
    ],
    
    "Song_And_Poem_Generation": [
        r"write (song|poem|lyrics|verse)",
        r"compose (song|poem|rhyme)",
        r"poetry|lyric|rhyme|stanza",
        r"song about|poem about",
        r"musical|rhythmic|poetic"
    ],
    
    "Character_Description_Generation": [
        r"describe character|character description",
        r"create character|generate character",
        r"character profile|backstory",
        r"personality traits|characteristics",
        r"physical description|appearance"
    ],
    
    "Code_Generation": [
        r"write code|generate code|create code",
        r"code for|program for|script for",
        r"implement|code implementation",
        r"function|class|method|program",
        r"coding|programming|development"
    ],
    
    "Code_Editing_And_Debugging": [
        r"fix (code|bug|error|issue)",
        r"debug|troubleshoot|solve",
        r"improve code|optimize code",
        r"error|bug|issue|problem",
        r"not working|fails|crashes"
    ],
    
    "Communication_Generation": [
        r"write (email|message|letter)",
        r"draft (email|message|response)",
        r"compose (email|message|reply)",
        r"formal|informal communication",
        r"correspondence|reply|respond"
    ],
    
    "Non_Fictional_Document_Generation": [
        r"write (resume|CV|report|essay)",
        r"create (document|paper|article)",
        r"generate (report|document)",
        r"professional document|paper",
        r"academic writing|technical writing"
    ],
    
    "Text_Editing": [
        r"edit|revise|improve|proofread",
        r"grammar|spelling|punctuation",
        r"rewrite|rephrase|reword",
        r"correction|fix text|improve text",
        r"style|clarity|coherence"
    ],
    
    "Comparison_Ranking_And_Recommendation": [
        r"compare|contrast|versus|vs",
        r"rank|rate|evaluate|assess",
        r"recommend|suggest|advise",
        r"best|better|worst|difference",
        r"pros and cons|advantages|disadvantages"
    ],
    
    "Brainstorming_And_Idea_Generation": [
        r"brainstorm|ideas|suggestions",
        r"generate ideas|come up with",
        r"creative|innovative|new ideas",
        r"possibilities|options|alternatives",
        r"think of|suggest|propose"
    ],
    
    "Information_Retrieval": [
        r"what is|tell me about|explain",
        r"find|search|look up|locate",
        r"information about|details about",
        r"fact|data|information",
        r"definition|meaning|description"
    ],
    
    "Problem_Solving": [
        r"solve|solution|resolve|fix",
        r"problem|issue|challenge",
        r"how to|help with|figure out",
        r"steps to|method to|way to",
        r"answer|solution|resolution"
    ],
    
    "Explanation_And_Practical_Advice": [
        r"explain|clarify|elaborate",
        r"how (to|do|can|should)",
        r"guide|tutorial|instructions",
        r"advice|tips|suggestions",
        r"help with|assistance with"
    ],
    
    "Personal_Advice": [
        r"advice|help|guidance",
        r"should I|what should|how should",
        r"personal|situation|dilemma",
        r"relationship|emotional|feelings",
        r"opinion|suggestion|recommendation"
    ],
    
    "Back_And_Forth_Role_Playing": [
        r"roleplay|role play|act as",
        r"pretend|simulate|scenario",
        r"play the role|be the|act like",
        r"character|personality|role",
        r"conversation|dialogue|interaction"
    ],
    
    "Answering_Multiple_Choice_Questions": [
        r"multiple choice|MCQ|quiz",
        r"choose|select|pick",
        r"options|choices|alternatives",
        r"correct answer|right answer",
        r"test|exam|assessment"
    ],
    
    "Translation": [
        r"translate|translation|convert",
        r"from.*to|into.*language",
        r"in (english|spanish|etc)",
        r"meaning in|say in",
        r"language|linguistic|interpretation"
    ],
    
    "General_Chitchat": [
        r"chat|talk|converse",
        r"casual|informal|friendly",
        r"hello|hi|hey",
        r"conversation|discussion",
        r"just wondering|curious"
    ]
}