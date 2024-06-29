// app/static/plan/script.js
let questions = [];
let answers = {};
let currentQuestion = null;
let turnstileToken = '';

document.getElementById('sendButton').addEventListener('click', async function() {
    await handleUserInput();
});

document.getElementById('userInput').addEventListener('keydown', async function(event) {
    if (event.key === 'Enter') {
        await handleUserInput();
    }
});

async function handleUserInput() {
    const userInput = document.getElementById('userInput').value;
    if (!userInput) return;

    appendMessage(userInput, 'user');
    document.getElementById('userInput').value = '';

    if (questions.length === 0) {
        await sendRequest(userInput);
    } else if (currentQuestion) {
        answers[currentQuestion.id] = userInput;
        displayNextQuestion();
    }
}

async function sendRequest(userInput) {
    if (!turnstileToken) {
        alert('請完成驗證');
        return;
    }

    const response = await fetch('/submit_request', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            request: userInput,
            'cf-turnstile-response': turnstileToken
        })
    });

    const data = await response.json();
    if (data.success) {
        questions = data.questions;
        displayNextQuestion();
    } else {
        alert('驗證失敗，請重試');
    }

    refreshTurnstile();
}

async function submitAnswers() {
    if (!turnstileToken) {
        alert('請完成驗證');
        return;
    }

    const response = await fetch('/submit_answers', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            answers: answers,
            'cf-turnstile-response': turnstileToken
        })
    });

    const data = await response.json();
    if (data.success) {
        if (data.success) {
            displayFinalPlan(data.plan);
        } else {
            questions = data.questions;
            displayNextQuestion();
        }
    } else {
        alert('驗證失敗，請重試');
    }

    refreshTurnstile();
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

    currentQuestion = questions.shift();
    const chatBox = document.getElementById('chatBox');
    const questionDiv = document.createElement('div');
    questionDiv.className = 'system';
    questionDiv.innerText = currentQuestion.text;

    currentQuestion.options.forEach(option => {
        const optionDiv = document.createElement('div');
        optionDiv.className = 'option-card';
        optionDiv.innerText = option;
        optionDiv.addEventListener('click', async () => {
            answers[currentQuestion.id] = option;
            appendMessage(option, 'user');
            disablePreviousOptions();
            if (questions.length === 0) {
                await submitAnswers();
            } else {
                displayNextQuestion();
            }
        });
        questionDiv.appendChild(optionDiv);
    });

    chatBox.appendChild(questionDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function disablePreviousOptions() {
    const optionCards = document.querySelectorAll('.option-card');
    optionCards.forEach(card => {
        card.style.pointerEvents = 'none';
        card.style.opacity = '0.5';
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

function turnstileCallback(token) {
    turnstileToken = token;
    console.log('Turnstile token received:', token);
}

function refreshTurnstile() {
    turnstileToken = '';
    turnstile.render('.cf-turnstile', {
        sitekey: '',
        callback: turnstileCallback,
        action: 'travel_plan'
    });
}
