// app/static/plan/script.js
let questions = [];
let newTrip = true;
let answers = {};
let currentQuestion = null;
let turnstileToken = '';
let socket = null;
let statusHistory = [];

$('#sendButton').click(async function() {
    await handleUserInput();
});

$('#userInput').keydown(async function(event) {
    if (event.key === 'Enter') {
        await handleUserInput();
    }
});

function disableInput() {
    $('#userInput').attr('disabled', true);
    $('#sendButton').attr('disabled', true);
}

function enableInput() {
    $('#userInput').attr('disabled', false);
    $('#sendButton').attr('disabled', false);
}

async function handleUserInput() {
    const userInput = $('#userInput').val();
    if (!userInput) return;

    appendMessage(userInput, 'user');
    $('#userInput').val('');
    disableInput();

    if (socket) {
        socket.emit('message', {message: userInput});
    }

    if (newTrip) {
        await sendRequest(userInput);
        newTrip = false;
    } else if (currentQuestion) {
        answers[currentQuestion.question] = userInput;
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
            enableInput();
            if (data.success) {
                showNotification("🌐 請求已處理完成", 5000);
                questions = JSON.parse(data.questions).questions;
                displayNextQuestion();
            } else {
                showError({title: '錯誤', message: '無法處理您的請求'});
            }
            refreshTurnstile();
        },
        error: function () {
            enableInput();
            showError({title: '錯誤', message: '無法處理您的請求'});
            refreshTurnstile();
        }
    });
}

async function submitAnswers() {
    if (!turnstileToken) {
        showError({title: '驗證失敗', message: '驗證金鑰無效，請稍後再試'});
        return;
    }

    disableInput();
    $.ajax({
        url: '/submit_answers',
        method: 'POST',
        timeout: 300000,
        contentType: 'application/json',
        data: JSON.stringify({
            answers: answers,
            'cf-turnstile-response': turnstileToken
        }),
        success: function(data) {
            enableInput();
            if (data.success) {
                if (data.new_question) {
                    questions = JSON.parse(data.questions).questions;
                    displayNextQuestion();
                } else {
                    clearLandmarks();
                    clearAttractions();
                    const response = JSON.parse(data.response);
                    if (response.sections && response.sections.length > 0) {
                        response.sections.forEach(section => {
                            if (section.landmarks) {
                                addLandmark(section.landmarks);
                            }
                            addAttraction(section);
                        });
                        displayFinalPlan(response.sections);

                        $('#mapContainer').addClass('active');
                        $('.container').addClass('map-active');
                        $('#toggleMap').addClass('icon-toggle active');
                        $('#attractionContainer').addClass('attractions-active');
                        $('.container').addClass('attractions-active');
                        $('#chatContainer').addClass('shrink');
                        $('#toggleAttractions').addClass('icon-toggle active');

                        setTimeout(() => {
                            adjustMapView(response.sections);
                        }, 750);

                    } else {
                        showError({title: '錯誤', message: '沒有找到旅行計劃的相關信息'});
                    }
                }
            } else {
                showError({title: '錯誤', message: data.error || '無法提交您的回答'});
            }
            refreshTurnstile();
        },
        error: function() {
            enableInput();
            showError({title: '錯誤', message: '無法提交您的回答'});
            refreshTurnstile();
        }
    });
}

function adjustMapView(sections) {
    const bounds = new mapboxgl.LngLatBounds();

    sections.forEach(section => {
        if (section.landmarks && section.landmarks.coordinates) {
            bounds.extend(section.landmarks.coordinates);
        }
    });

    if (!bounds.isEmpty()) {
        map.fitBounds(bounds, {
            padding: 200
        });
    }
}

function appendMessage(message, sender) {
    if (sender !== 'system' && sender !== 'user') {
        appendStatusMessage(message);
        return;
    }
    const messageDiv = $('<div>').addClass(sender).text(message);
    $('#chatBox').append(messageDiv).scrollTop($('#chatBox')[0].scrollHeight);
}

function displayNextQuestion() {
    if (questions.length === 0) return;

    currentQuestion = questions.shift();
    const questionDiv = $('<div>').addClass('system').text(currentQuestion.question);

    if (currentQuestion.options && currentQuestion.options.length > 0) {
        currentQuestion.options.forEach(option => {
            const optionDiv = $('<div>').addClass('option-card').text(option).click(async () => {
                answers[currentQuestion.question] = option;
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
    } else {
        questionDiv.append($('<div>').addClass('option-card').text('請輸入您的回答'));
    }

    $('#chatBox').append(questionDiv).scrollTop($('#chatBox')[0].scrollHeight);
}

function disablePreviousOptions() {
    $('.option-card').css({'pointer-events': 'none', 'opacity': '0.5'});
}

function displayFinalPlan(sections) {
    sections.forEach(section => {
        const planDiv = $('<div>').addClass('system').html(`
            <h2>${section.title}</h2>
            <p>${section.description}</p>
            <img src="${section.image}" alt="${section.title}" class="plan-image" onerror="$(this).addClass('hidden')">
            <p>位置: ${section.location}</p>
            <p>交通方式: ${section.transportation}</p>
            <p>住宿: ${section.accommodation}</p>
            <p>餐廳: ${section.restaurant}</p>
            <p>活動: ${section.activity}</p>
            <p>時間: ${section.time}</p>
        `);
        $('#chatBox').append(planDiv).scrollTop($('#chatBox')[0].scrollHeight);
    });
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
            appendMessage(data.message, data.role);
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

function appendStatusMessage(message) {
    const timestamp = new Date().toLocaleTimeString();
    statusHistory.push({timestamp, message});

    const lastMessage = $('#chatBox > div').last();
    if (lastMessage.hasClass('status')) {
        lastMessage.find('.status-text').text(message);
        lastMessage.find('.status-history').append(`<p>${timestamp} : ${message}</p>`);
    } else {
        const statusDiv = $(`
            <div class="status" style="background-color: #fbf3dc; padding: 10px; border-radius: 5px; margin: 5px 0; position: relative;">
                <div class="status-text" style="display: inline;">${message}</div>
                <i class="fas fa-history toggle-history" style="cursor: pointer;"></i>
                <div class="status-history" style="display: none; margin-top: 5px;">
                    <p>${timestamp} : ${message}</p>
                </div>
            </div>
        `);
        $('#chatBox').append(statusDiv).scrollTop($('#chatBox')[0].scrollHeight);

        statusDiv.find('.toggle-history').click(function () {
            const historyDiv = $(this).next('.status-history');
            historyDiv.slideToggle();
            $(this).toggleClass('active');
        });
    }
}

// Container icon buttons
$(document).ready(function() {
    $('#toggleMap').click(function() {
        const mapContainer = $('#mapContainer');
        mapContainer.toggleClass('active');
        $('.container').toggleClass('map-active');
        $(this).toggleClass('icon-toggle active');

        const attractionContainer = $('#attractionContainer');
        if (attractionContainer.hasClass('attractions-active')) {
            attractionContainer.removeClass('attractions-active');
            $('#toggleAttractions').removeClass('icon-toggle active');
            $('#chatContainer').removeClass('shrink');
        }
    });

    $('#toggleAttractions').click(function() {
        const attractionContainer = $('#attractionContainer');
        attractionContainer.toggleClass('attractions-active');
        $('.container').toggleClass('attractions-active');
        $('#chatContainer').toggleClass('shrink');
        $(this).toggleClass('icon-toggle active');

        if (attractionContainer.hasClass('attractions-active')) {
            $('#mapContainer').addClass('active');
            $('#toggleMap').addClass('icon-toggle active');
            $('.container').addClass('map-active');
        }
    });

    $('#toggleOverview').click(function() {
        $(this).toggleClass('icon-toggle active');
    });

    $('#closeDetail').click(function() {
        $('#detailContainer').removeClass('visible').addClass('hidden');
    });
});

function showAttractionDetails(title, description, image, location, transportation, accommodation, restaurant, activity, youtubeUrls) {
    $('#detailTitle').text(title);
    $('#detailImage').attr('src', image).on('error', function() {
        $(this).addClass('hidden');
        $('#detailImageContainer').addClass('hidden');
        $('#detailText').removeClass('with-image');
    }).removeClass('hidden');
    $('#detailDescription').text(description);
    $('#detailLocation').html(`位置: ${location}`);
    $('#detailTransport').html(`交通方式: ${transportation}`);
    $('#detailAccommodation').html(`住宿: ${accommodation}`);
    $('#detailRestaurant').html(`餐廳: ${restaurant}`);
    $('#detailActivity').html(`活動: ${activity}`);

    $('#detailVideos').empty();

    if (Array.isArray(youtubeUrls) && youtubeUrls.length > 0) {
        youtubeUrls.forEach(video => {
            const videoId = extractYouTubeVideoId(video.url);
            const videoFrame = $(`
                <iframe class="detail-video" src="https://www.youtube.com/embed/${videoId}" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
            `);
            $('#detailVideos').append(videoFrame);
        });
    } else {
        $('#detailVideos').append('<p>沒有可用的影片</p>');
    }

    $('#detailContainer').removeClass('hidden').addClass('visible');
}

function addAttraction(section) {
    const attractionCard = $(`
        <div class="attraction-card" onclick='showAttractionDetails(
            "${section.title.replace(/'/g, "\\'")}", 
            "${section.description.replace(/'/g, "\\'")}", 
            "${section.image.replace(/'/g, "\\'")}",
            "${section.location.replace(/'/g, "\\'")}",
            "${section.transportation.replace(/'/g, "\\'")}",
            "${section.accommodation.replace(/'/g, "\\'")}",
            "${section.restaurant.replace(/'/g, "\\'")}",
            "${section.activity.replace(/'/g, "\\'")}",
            ${JSON.stringify(section.youtube_url).replace(/'/g, "\\'")}
        )'>
            <div class="attraction-card-content">
                <h3>${section.title}</h3>
                <p>${section.description}</p>
            </div>
        </div>
    `);
    $('#attractionContainer').append(attractionCard);
}

function clearAttractions() {
    $('#attractionContainer').empty();
}

function extractYouTubeVideoId(url) {
    const regExp = /^.*(youtu.be\/|v\/|\/u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
    const match = url.match(regExp);
    return (match && match[2].length == 11) ? match[2] : null;
}
