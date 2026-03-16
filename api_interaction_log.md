============================================================
REQUEST 1: Submit Learning Topic to Agent
============================================================
curl --location 'http://localhost:3773' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {{api_key}}' \
--data '{
  "jsonrpc": "2.0",
  "method": "message/send",
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "params": {
    "configuration": {
      "acceptedOutputModes": ["text"]
    },
    "message": {
      "messageId": "123e4567-e89b-12d3-a456-426614174001",
      "contextId": "123e4567-e89b-12d3-a456-426614174002",
      "taskId": "5b1c9a0e-6a3f-4c2e-b4d2-8f9c0e1a0003",
      "kind": "message",
      "role": "user",
      "content": "Create a curriculum for learning Python for Data Science",
      "parts": [
        {
          "kind": "text",
          "text": "Create a curriculum for learning Python for Data Science"
        }
      ]
    }
  }
}'

============================================================
RESPONSE 1: Task Acknowledged (Async processing begins)
============================================================
{
    "jsonrpc": "2.0",
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "result": {
        "id": "5b1c9a0e-6a3f-4c2e-b4d2-8f9c0e1a0003",
        "context_id": "123e4567-e89b-12d3-a456-426614174002",
        "kind": "task",
        "status": {
            "state": "submitted",
            "timestamp": "2026-03-16T11:08:38.286160+00:00"
        },
        "history": [
            {
                "message_id": "123e4567-e89b-12d3-a456-426614174001",
                "context_id": "123e4567-e89b-12d3-a456-426614174002",
                "task_id": "5b1c9a0e-6a3f-4c2e-b4d2-8f9c0e1a0003",
                "kind": "message",
                "parts": [
                    {
                        "kind": "text",
                        "text": "Create a curriculum for learning Python for Data Science"
                    }
                ],
                "role": "user"
            }
        ]
    }
}

============================================================
REQUEST 2: Poll for Task Completion
============================================================
curl --location 'http://localhost:3773' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {{api_key}}' \
--data '{
  "jsonrpc": "2.0",
  "method": "tasks/get",
  "params": {
    "taskId": "5b1c9a0e-6a3f-4c2e-b4d2-8f9c0e1a0003"
  },
  "id": "123e4567-e89b-12d3-a456-426614174005"
}'

============================================================
RESPONSE 2: Task Completed (Compiled by Multi-Agent Graph)
============================================================
{
    "jsonrpc": "2.0",
    "id": "123e4567-e89b-12d3-a456-426614174005",
    "result": {
        "id": "5b1c9a0e-6a3f-4c2e-b4d2-8f9c0e1a0003",
        "context_id": "123e4567-e89b-12d3-a456-426614174002",
        "kind": "task",
        "status": {
            "state": "completed",
            "timestamp": "2026-03-16T11:09:15.123456+00:00"
        },
        "history": [
            {
                "message_id": "123e4567-e89b-12d3-a456-426614174001",
                "context_id": "123e4567-e89b-12d3-a456-426614174002",
                "task_id": "5b1c9a0e-6a3f-4c2e-b4d2-8f9c0e1a0003",
                "kind": "message",
                "parts": [
                    {
                        "kind": "text",
                        "text": "Create a curriculum for learning Python for Data Science"
                    }
                ],
                "role": "user"
            },
            {
                "role": "assistant",
                "parts": [
                    {
                        "kind": "text",
                        "text": "# 🎓 AI Teaching Team: Python for Data Science\n---\n## 🧠 Knowledge Base\nPython has become the lingua franca of Data Science due to its readability, massive open-source community, and powerful numerical computation libraries. A solid data science foundation in Python requires mastering core syntax, data manipulation (Pandas), numerical computing (NumPy), data visualization (Matplotlib/Seaborn), and introductory machine learning (Scikit-Learn).\n---\n## 🗺️ Learning Roadmap\n**Phase 1: Core Python (Weeks 1-2)**\n- Data types, control flow, functions, and list comprehensions.\n- Object-Oriented Programming (OOP) basics.\n\n**Phase 2: Data Manipulation (Weeks 3-4)**\n- NumPy: Arrays, vectorization, and broadcasting.\n- Pandas: DataFrames, Series, filtering, grouping, and handling missing data.\n\n**Phase 3: Exploratory Data Analysis (Weeks 5-6)**\n- Matplotlib: Core plotting logic.\n- Seaborn: Statistical data visualization.\n---\n## 📚 Resource Library\n- **Documentation:** Pandas Official Docs, Scikit-Learn User Guide.\n- **Books:** 'Python for Data Analysis' by Wes McKinney (Creator of Pandas).\n- **Datasets:** Kaggle (Titanic Dataset is recommended for beginners).\n---\n## ✍️ Practice Workbook\n**Exercise 1: Pandas Data Cleaning**\nLoad a CSV file containing housing data. Write a script to fill all missing values in the 'Age' column with the median age, and drop any rows where 'Price' is NaN.\n\n**Exercise 2: NumPy Broadcasting**\nCreate a 3x3 NumPy array of random integers. Subtract the mean of each row from its respective elements without using a standard Python `for` loop."
                    }
                ],
                "kind": "message",
                "message_id": "8a7b6c5d-4e3f-2g1h-0i9j-8k7l6m5n4o3p",
                "task_id": "5b1c9a0e-6a3f-4c2e-b4d2-8f9c0e1a0003",
                "context_id": "123e4567-e89b-12d3-a456-426614174002"
            }
        ]
    }
}
