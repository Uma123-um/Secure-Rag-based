from vector_store import vector_db


def retrieve(question, user):
    department  = user["department"]

    results = vector_db.similarity_search(
        question,
        k=3,
        filter = {
            "department": department
        }
    )

    return results