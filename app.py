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


title = "Scripture Semantic Search"

bible_books = [data[i]['name'] for i in range(len(data))]

with gr.Blocks() as demo:

    gr.Markdown(f'<center><h1>{title}</h1></center>')

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
