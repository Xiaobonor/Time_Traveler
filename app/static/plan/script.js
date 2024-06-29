let questions = [];
let answers = {};

document.getElementById('sendButton').addEventListener('click', async function() {
    const userInput = document.getElementById('userInput').value;
    if (!userInput) return;

    appendMessage(userInput, 'user');
    document.getElementById('userInput').value = '';

    if (questions.length === 0) {
        const response = await fetch('/submit_request', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ request: userInput })
        });

        const data = await response.json();
        questions = data.questions;
    }

    displayNextQuestion();
});

async function submitAnswers() {
    const response = await fetch('/submit_answers', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ answers: answers })
    });

    const data = await response.json();
    if (data.completed) {
        displayFinalPlan(data.plan);
    } else {
        questions = data.questions;
        displayNextQuestion();
    }
}

function appendMessage(message, sender) {
    const chatBox = document.getElementById('chatBox');
    const messageDiv = document.createElement('div');
    messageDiv.className = sender;
    messageDiv.innerText = message;
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function displayNextQuestion() {
    if (questions.length === 0) return;

    const question = questions.shift();
    const chatBox = document.getElementById('chatBox');
    const questionDiv = document.createElement('div');
    questionDiv.className = 'system';
    questionDiv.innerText = question.text;

    question.options.forEach(option => {
        const optionDiv = document.createElement('div');
        optionDiv.className = 'option-card';
        optionDiv.innerText = option;
        optionDiv.addEventListener('click', () => {
            answers[question.id] = option;
            appendMessage(option, 'user');
            displayNextQuestion();
        });
        questionDiv.appendChild(optionDiv);
    });

    chatBox.appendChild(questionDiv);
    chatBox.scrollTop = chatBox.scrollHeight;

    document.getElementById('userInput').addEventListener('keydown', function (event) {
        if (event.key === 'Enter') {
            const userInput = document.getElementById('userInput').value;
            if (!userInput) return;

            answers[question.id] = userInput;
            appendMessage(userInput, 'user');
            document.getElementById('userInput').value = '';
            displayNextQuestion();
        }
    });
}

function displayFinalPlan(plan) {
    const chatBox = document.getElementById('chatBox');
    const planDiv = document.createElement('div');
    planDiv.className = 'system';
    planDiv.innerHTML = `
        <h2>您的旅行計劃</h2>
        <p>行程安排: ${plan.schedule}</p>
        <p>景點: ${plan.attractions}</p>
        <p>餐廳: ${plan.restaurants}</p>
        <p>住宿: ${plan.accommodations}</p>
    `;
    chatBox.appendChild(planDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}
