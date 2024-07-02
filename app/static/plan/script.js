// app/static/plan/script.js
let questions = [];
let newTrip = true;
let answers = {};
let currentQuestion = null;
let turnstileToken = '';
let socket = null;

$('#sendButton').click(async function() {
    await handleUserInput();
});

$('#userInput').keydown(async function(event) {
    if (event.key === 'Enter') {
        await handleUserInput();
    }
});

async function handleUserInput() {
    const userInput = $('#userInput').val();
    if (!userInput) return;

    appendMessage(userInput, 'user');
    $('#userInput').val('');

    if (socket) {
        socket.emit('message', { message: userInput });
    }

    if (newTrip) {
        await sendRequest(userInput);
        newTrip = false;
    } else if (currentQuestion) {
        answers[currentQuestion.id] = userInput;
        if (questions.length === 0) {
            await submitAnswers();
        } else {
            displayNextQuestion();
        }
    }
}

async function sendRequest(userInput) {
    while (!turnstileToken) {
        await new Promise(resolve => setTimeout(resolve, 500));
    }

    $('#chatBox').removeClass('loading');
    showNotification("🌐 已發送您的請求，處理中...", 5000);

    $.ajax({
        url: '/submit_request',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            request: userInput,
            'cf-turnstile-response': turnstileToken
        }),
        success: function(data) {
            if (data.success) {
                showNotification("🌐 請求已處理完成", 5000);
                questions = data.questions;
                displayNextQuestion();
            } else {
                showError({ title: '錯誤', message: '無法處理您的請求' });
            }
            refreshTurnstile();
        },
        error: function() {
            showError({ title: '錯誤', message: '無法處理您的請求' });
            refreshTurnstile();
        }
    });
}

async function submitAnswers() {
    if (!turnstileToken) {
        showError({ title: '驗證失敗', message: '驗證金鑰無效，請稍後再試' });
        return;
    }

    $.ajax({
        url: '/submit_answers',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            answers: answers,
            'cf-turnstile-response': turnstileToken
        }),
        success: function(data) {
            if (data.success) {
                displayFinalPlan(data.plan);
            } else {
                questions = data.questions;
                displayNextQuestion();
            }
            refreshTurnstile();
        },
        error: function() {
            showError({ title: '錯誤', message: '無法提交您的回答' });
            refreshTurnstile();
        }
    });
}

function appendMessage(message, sender) {
    const messageDiv = $('<div>').addClass(sender).text(message);
    $('#chatBox').append(messageDiv).scrollTop($('#chatBox')[0].scrollHeight);
}

function displayNextQuestion() {
    if (questions.length === 0) return;

    currentQuestion = questions.shift();
    const questionDiv = $('<div>').addClass('system').text(currentQuestion.text);

    currentQuestion.options.forEach(option => {
        const optionDiv = $('<div>').addClass('option-card').text(option).click(async () => {
            answers[currentQuestion.id] = option;
            appendMessage(option, 'user');
            disablePreviousOptions();
            if (questions.length === 0) {
                await submitAnswers();
            } else {
                displayNextQuestion();
            }
        });
        questionDiv.append(optionDiv);
    });

    $('#chatBox').append(questionDiv).scrollTop($('#chatBox')[0].scrollHeight);
}

function disablePreviousOptions() {
    $('.option-card').css({ 'pointer-events': 'none', 'opacity': '0.5' });
}

function displayFinalPlan(plan) {
    const planDiv = $('<div>').addClass('system').html(`
        <h2>您的旅行計劃</h2>
        <p>行程安排: ${plan.schedule}</p>
        <p>景點: ${plan.attractions}</p>
        <p>餐廳: ${plan.restaurants}</p>
        <p>住宿: ${plan.accommodations}</p>
    `);
    $('#chatBox').append(planDiv).scrollTop($('#chatBox')[0].scrollHeight);
}

function turnstileCallback(token) {
    turnstileToken = token;
    console.log('Turnstile token received:', token);
    $('#chatBox').removeClass('loading');

    if (newTrip) {
        socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

        socket.on('connect', () => {
            console.log('Connected to the server');
        });

        socket.on('disconnect', () => {
            appendMessage('🌐 與伺服器斷開連接', 'system');
            console.log('Disconnected from the server');
        });

        socket.on('status_update', (data) => {
            appendMessage(data.message, 'system');
        });

        socket.on('message', (data) => {
            appendMessage(data.message, 'system');
        });
    }
}

function refreshTurnstile() {
    turnstileToken = '';
    turnstile.render('.cf-turnstile', {
        sitekey: '',
        callback: turnstileCallback,
        action: 'travel_plan'
    });
}
