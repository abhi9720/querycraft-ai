# Product Document: QueryCraftAI

## 1. Introduction: Your Personal Data Analyst

QueryCraftAI is an open-source project that bridges the gap between complex databases and natural human language. It provides an intuitive chat interface that allows anyone—from developers and data analysts to business stakeholders—to ask questions about their data in plain English and receive ready-to-use SQL queries and clear, understandable explanations in return.

**Our vision is to democratize data access, making it as simple as having a conversation.**

## 2. The Problem: Data is Hard to Access

Databases are the heart of modern applications, yet accessing the information they hold often requires specialized knowledge of SQL. This creates a bottleneck where:

*   **Developers** spend valuable time writing and debugging complex queries instead of building features.
*   **Data Analysts** are overwhelmed with requests for simple data pulls and reports.
*   **Non-technical users** (like product managers, marketers, or executives) are unable to self-serve their data needs, leading to delays and missed opportunities.

## 3. The Solution: A Conversational AI for Databases

QueryCraftAI is an intelligent system that understands user intent and the underlying database schema. It acts as a translator, converting natural language questions into precise SQL code.

By integrating this agent, an organization can empower its entire team to explore data, gain insights, and make data-driven decisions independently.

## 4. Key Features

*   **Natural Language Querying:** Ask questions in plain English, just as you would to a person.
*   **Intelligent Schema Detection:** The agent automatically identifies the relevant tables and columns needed to answer your question.
*   **Accurate SQL Generation:** Generates a precise, executable SQL query tailored to your request.
*   **Plain English Explanations:** Every generated query is accompanied by a step-by-step explanation, making it a great learning tool for those new to SQL.
*   **Simple Web Interface:** A clean, user-friendly chat interface for easy interaction.
*   **Extensible Agent-Based Architecture:** The modular design allows developers to easily extend the agent\'s capabilities or adapt it to different SQL dialects.

## 5. How It Works: System Architecture

The application uses a multi-agent system where each agent has a specialized role. The process is orchestrated by a backend Flask API and presented to the user through a simple frontend.

![QueryCraftAI Architecture](assets/architecture.png)

### Dashboard / User Interface Screenshots

#### Main Chat Interface
![Main Chat Interface](assets/dashboard-1.png)

#### SQL Query Result
![Query Result](assets/dashboard-2.png)

#### Additional Features
![Dashboard Analytics](assets/dashboard-3.png)

## 6. Use Cases

*   **Rapid Prototyping:** Developers can quickly generate complex queries needed for new application features.
*   **Data Exploration:** Analysts can perform ad-hoc analysis without writing boilerplate SQL.
*   **Business Intelligence:** Business users can get answers to questions like "How many new users signed up last week?" without waiting for an analyst.
*   **Learning SQL:** Junior developers or students can use the agent as a tool to learn SQL by seeing how their questions translate into code.

## 7. Getting Started

To get a local instance of the agent running, follow these steps:

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Run the development server:**
    ```bash
    ./devserver.sh
    ```
3.  **Open your browser** and navigate to the local URL provided.

## 8. Roadmap: The Future of Conversational Data

This project is just the beginning. Our future plans include:

*   [ ] **Support for More SQL Dialects:** Adding support for PostgreSQL, MySQL, and others.
*   [ ] **Data Visualization:** Automatically generating charts and graphs to visualize the query results.
*   [ ] **Query History & Saving:** Allowing users to save and reuse frequently asked questions.
*   [ ] **Advanced Data Context:** Enabling the agent to understand more complex relationships and business-specific logic.
*   [ ] **Integration with BI Tools:** Connecting the agent to popular BI platforms.

## 9. Contributing

This is an open-source project, and we welcome contributions from the community! Whether it\'s a bug fix, a new feature, or improved documentation, your help is valued. Please see our `CONTRIBUTING.md` file for guidelines.

## 10. License

QueryCraftAI is licensed under the MIT License.
