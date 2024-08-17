from fastapi import FastAPI, Form
import pickle
import numpy as np

try:
    popular_df = pickle.load(open('popular.pkl', 'rb'))
    pt = pickle.load(open('pt.pkl', 'rb'))
    books = pickle.load(open('books.pkl', 'rb'))
    similarity_scores = pickle.load(open('similarity_scores.pkl', 'rb'))
except Exception as e:
    print(f"Error loading files: {e}")
    raise e

app = FastAPI()

@app.get("/books")
async def get_books():
    try:
        response_data={
            "book_name": list(popular_df['Book-Title'].values),
            "author" : list(popular_df['Book-Author'].values),
            "image":list(popular_df['Image-URL-M'].values),
            "votes":  list(map(int, popular_df['num_ratings'].values)),
            "rating":list(popular_df['avg_ratings'].values)
        }
        return response_data
    except Exception as e:
        print(f"Error in get_books: {e}")
        #raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/recommend_books")
async def recommend_books(user_input: str = Form(...)):
    try:
        index = np.where(pt.index == user_input)[0][0]
        similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:7]

        recommendations = []
        for i in similar_items:
            item = {}
            temp_df = books[books['Book-Title'] == pt.index[i[0]]]
            item["book_name"] = list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values)[0]
            item["author"] = list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values)[0]
            item["image"] = list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values)[0]
            recommendations.append(item)

        return {"recommendations": recommendations}
    
    except IndexError:
        return {"error": "Book not found"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, debug=True)
