from langchain_community.document_loaders import PyMuPDFLoader

loader = PyMuPDFLoader("data\ORGANIC FARMING - CULTIVATING SUSTAINABLE AGRICULTURE.pdf")

documents = loader.load()
print(documents[1])