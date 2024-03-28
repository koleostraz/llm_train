import os
import openai
from dotenv import load_dotenv, find_dotenv 
from langchain.llms import OpenAI
from langchain.output_parsers import ResponseSchema
from langchain.output_parsers import StructuredOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor 


load_dotenv(find_dotenv())
openai.api_key = os.environ["OPENAI_API_KEY"]
token = os.environ["TOKEN"]

llm = OpenAI(model_name="text-ada-001")

sentiment_schema = ResponseSchema(
    name="sentiment",
    description="Is the text positive, neutral or negative? Only provide these words",
)
subject_schema = ResponseSchema(
    name="subject", description="What subject is the text about? Use exactly one word."
)

response_schemas = [sentiment_schema, subject_schema]

parser = StructuredOutputParser.from_response_schemas(response_schemas)
format_instructions = parser.get_format_instructions()

text = """
The men's high jump event at the 2020 Summer Olympics took place between 30 July and 1 August 2021 at the Olympic Stadium.
33 athletes from 24 nations competed; the total possible number depended on how many nations would use universality places 
to enter athletes in addition to the 32 qualifying through mark or ranking (no universality places were used in 2021).
Italian athlete Gianmarco Tamberi along with Qatari athlete Mutaz Essa Barshim emerged as joint winners of the event following
a tie between both of them as they cleared 2.37m. Both Tamberi and Barshim agreed to share the gold medal in a rare instance
where the athletes of different nations had agreed to share the same medal in the history of Olympics. 
Barshim in particular was heard to ask a competition official "Can we have two golds?" in response to being offered a 
'jump off'. Maksim Nedasekau of Belarus took bronze. The medals were the first ever in the men's high jump for Italy and 
Belarus, the first gold in the men's high jump for Italy and Qatar, and the third consecutive medal in the men's high jump
for Qatar (all by Barshim). Barshim became only the second man to earn three medals in high jump, joining Patrik Sjöberg
of Sweden (1984 to 1992)."""

template = """
Evaluate the question and answer the question using text.
sentiment: is the question in a positive, neutral or negative sentiment?
answer: answer the question as truthfully as possible using the provided text, and if the answer is not contained within the text below, say "I don't know".

Just return the JSON, do not add ANYTHING, NO INTERPRETATION!

text: {text}
question: {input}


{format_instructions}

"""

prompt = ChatPromptTemplate.from_template(template=template)

format_instructions = parser.get_format_instructions()

bot = Bot(token=token)
dp = Dispatcher(bot=bot)

@dp.message_handler()
async def sentiment(message: types.Message):
    messages = prompt.format_messages(
        text = text,
        input = message,
        format_instructions = format_instructions,)
    chat = ChatOpenAI(temperature=0.0)
    response = chat(messages)
    response = chat(messages)
    output_dict = parser.parse(response.content)

    if output_dict['sentiment'] == 'negative': print('ACTION')
    else: await bot.send_message(message.from_user.id, output_dict['subject'])
