# NISM Research Analyst Mock Test

# List of questions, options, and correct answers
questions = [
    {
        "question": "1. What is the primary role of a Research Analyst?",
        "options": [
            "A. To trade stocks frequently",
            "B. To understand and evaluate companies and industries",
            "C. To provide legal advice",
            "D. To manage bank branches"
        ],
        "answer": "B"
    },
    {
        "question": "2. Which of the following is a fundamental analysis tool?",
        "options": [
            "A. Moving Averages",
            "B. P/E Ratio",
            "C. RSI",
            "D. MACD"
        ],
        "answer": "B"
    },
    {
        "question": "3. Which economic indicator reflects the overall price level changes?",
        "options": [
            "A. GDP Growth",
            "B. CPI (Consumer Price Index)",
            "C. P/E Ratio",
            "D. Exchange Rate"
        ],
        "answer": "B"
    },
    {
        "question": "4. Which type of report is prepared by analysts after evaluating a company?",
        "options": [
            "A. Research Report",
            "B. Audit Report",
            "C. Credit Report",
            "D. Compliance Report"
        ],
        "answer": "A"
    },
    {
        "question": "5. What does 'Break of Structure' in technical analysis indicate?",
        "options": [
            "A. Change in market trend",
            "B. Annual financial statement",
            "C. Dividend announcement",
            "D. IPO listing"
        ],
        "answer": "A"
    }
]

# Function to run the mock test
def run_mock_test():
    score = 0
    print("Welcome to NISM Research Analyst Mock Test!\n")
    for q in questions:
        print(q["question"])
        for opt in q["options"]:
            print(opt)
        answer = input("Enter your answer (A/B/C/D): ").strip().upper()
        if answer == q["answer"]:
            print("Correct!\n")
            score += 1
        else:
            print(f"Wrong! Correct answer is {q['answer']}\n")
    print(f"Test Completed! Your Score: {score}/{len(questions)}")
    percentage = (score/len(questions))*100
    print(f"Percentage: {percentage:.2f}%")
    if percentage >= 60:
        print("You Passed the Mock Test! 🎉")
    else:
        print("You Did Not Pass. Keep Practicing! 💪")

# Run the test
if __name__ == "__main__":
    run_mock_test()
