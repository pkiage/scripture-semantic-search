import gradio as gr

from pathlib import Path
import pandas as pd
import json

# import numpy as np

import chromadb
from chromadb.config import Settings


# Get path to /data/interim
data_interim_dir = Path("data") / Path("interim")

filepath = data_interim_dir / Path("en_bbe.json")

with open(filepath) as f:
    data = json.load(f)

book_names = [data[i]["name"] for i in range(len(data))]

book_names_filter = [data[i]["name"].lower().replace(" ", "")
                     for i in range(len(data))]


filepath = str(data_interim_dir / Path("ChromaDB"))

chroma_client = chromadb.Client(
    Settings(chroma_db_impl="duckdb+parquet", persist_directory=filepath)
)

collection = chroma_client.get_or_create_collection(name="bible")


def result_to_df_bible(result):
    result_df = pd.DataFrame.from_dict(result)
    result_df = result_df.drop(
        ["embeddings", "distances", "metadatas"], axis=1)
    columns = list(result_df.columns)
    result_df = result_df.explode(columns)

    return result_df.rename(columns={"ids": "Reference", "documents": "Verse", })


def result_to_df_book(result):
    result_df = pd.DataFrame.from_dict(result)
    result_df = result_df.drop(["embeddings", "metadatas"], axis=1)
    columns = list(result_df.columns)
    result_df = result_df.explode(columns)

    return result_df.rename(columns={"ids": "Reference", "documents": "Verse"})


def semantic_search_bible(query, top_n):
    query = [query]
    result = collection.query(
        query_texts=query,
        n_results=int(top_n) * 2,
        include=["metadatas",
                 "documents"]
    )

    return result_to_df_bible(result)


def semantic_search_bible_book(query, top_n, book_filter):
    query = [query]
    book_filter = book_filter.lower().replace(" ", "")
    result = collection.query(
        query_texts=query,
        n_results=int(top_n),
        where={"book": book_filter},
        include=["metadatas",
                 "documents",
                 "distances"]
    )

    return result_to_df_book(result)


def semantic_search_bible_book_chapter(query, top_n, book_filter, chapter_filter):
    query = [query]
    book_filter = book_filter.lower().replace(" ", "")
    result = collection.query(
        query_texts=query,
        n_results=int(top_n),
        where={"book": book_filter,
               "chapter": str(chapter_filter)},
        include=["metadatas",
                 "documents",
                 "distances"]
    )

    return result_to_df_book(result)


def get_book_chapters(book_filter):
    book_number = bible_books.index(book_filter)
    return len(data[book_number]['chapters'])

bible_books = [data[i]['name'] for i in range(len(data))]

title = "Scripture Semantic Search"

d1 = "**Scripture [semantic search](https://en.wikipedia.org/wiki/Semantic_search) considerations:**"

d2 = "\n - Works better with high level concepts (e.g. Peace, Love, etc.), performance on names and objects could be improved"

d3 = "\n - Uses [ChromaDB's](https://docs.trychroma.com/embeddings) [default](https://github.com/chroma-core/chroma/blob/main/chromadb/utils/embedding_functions.py) [Sentence Transformer](https://www.sbert.net/) to generate vector embeddings with 4x less dimensions (384) than [OpenAI's](https://platform.openai.com/docs/guides/embeddings/what-are-embeddings) text-embedding-ada-002 (1536)"

d4 = "\n - Embeddings are created from [Bible in Basic English (BBE)](https://en.wikipedia.org/wiki/Bible_in_Basic_English) translations with data obtained [here](https://github.com/thiagobodruk/bible/blob/master/json/en_bbe.json) (different transalations have different phrasing)"

d5 = "\n \n *The information provided on this website does not, and is not intended to, constitute advice; instead, all information, content, and materials available on this site are for general informational purposes only. This tool is intended to showcase the potential of semantic search and not to replace study using other techniques and resources. The semantic search is not 100 % accurate.*"

description = d1 + d2 + d3 + d4 + d5

with gr.Blocks() as demo:

    gr.Markdown(f'<center><h1>{title}</h1></center>')

    gr.Markdown(description)

    with gr.Tab("Search: Bible"):
        query = gr.Textbox(label="Query")

        top_n = gr.Number(value=5, precision=0,
                          label="Find top n semantic matches")

        search_outputs = [gr.Dataframe(headers=["Reference", "Verse"])]

        btn = gr.Button(value="Semantic Search")

        btn.click(fn=semantic_search_bible,
                  inputs=[query,
                          top_n],
                  outputs=search_outputs)

    with gr.Tab("Search: Bible Book"):
        book_filter = gr.Dropdown(choices=bible_books, label="Book")

        query = gr.Textbox(label="Query")

        top_n = gr.Number(value=5,
                          precision=0,
                          label="Find top n semantic matches")

        search_outputs = [gr.Dataframe(headers=["Reference", "Verse"])]

        btn = gr.Button(value="Semantic Search")

        btn.click(fn=semantic_search_bible_book,
                  inputs=[query,
                          top_n,
                          book_filter],
                  outputs=search_outputs)

    with gr.Tab("Search: Bible Book Chapter"):

        book_filter = gr.Dropdown(
            choices=bible_books,
            label="Book")

        chapt_output = gr.Textbox(label="Total chapters in book")

        chapt = book_filter.change(fn=get_book_chapters,
                                   inputs=book_filter,
                                   outputs=chapt_output)

        chapter_filter = gr.Number(value=1,
                                   precision=0,
                                   label="Select chapter in book")

        query = gr.Textbox(label="Query")

        top_n = gr.Number(value=5,
                          precision=0,
                          label="Find top n semantic matches")

        search_outputs = [gr.Dataframe(headers=["Reference", "Verse"])]

        btn = gr.Button(value="Semantic Search")

        btn.click(fn=semantic_search_bible_book_chapter,
                  inputs=[query,
                          top_n,
                          book_filter,
                          chapter_filter],
                  outputs=search_outputs)

demo.launch(server_port=8080)