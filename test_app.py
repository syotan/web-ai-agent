import chainlit as cl

@cl.on_chat_start
async def start():
    await cl.Message(content="こんにちは！Web-AI-Agentへようこそ！").send()

@cl.on_message
async def main(message: cl.Message):
    await cl.Message(content=f"受け取ったメッセージ: {message.content}").send()
