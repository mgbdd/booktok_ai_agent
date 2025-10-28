from langchain_core.output_parsers import StrOutputParser, JsonOutputParser


'''

вставить в готового gemini агента 

def _make_json_answer(self, summary : str, ideas : str) -> str:
        """
        This tool unites previous results into one json answer
        """
        system_template = get_prompt(os.getenv("JSON_PROMPT"))
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_template),
                ("user", "{summary}, {ideas}")
            ]
        )
        chain = prompt | self.llm | JsonOutputParser()
        result = chain.invoke({"summary" : summary, "ideas" : ideas})
        return result
    

'''