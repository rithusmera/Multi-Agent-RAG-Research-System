from graph.workflow import app

result = app.invoke({
    'query': 'What is RAG?'
})

print(result['final_answer'])