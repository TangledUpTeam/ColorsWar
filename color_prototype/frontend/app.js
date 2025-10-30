// Color Prototype - 프론트엔드 JavaScript

// 탭 전환
function switchTab(tabNum) {
    // 모든 탭 비활성화
    document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    // 선택된 탭 활성화
    document.querySelectorAll('.tab-button')[tabNum - 1].classList.add('active');
    document.getElementById(`tab${tabNum}`).classList.add('active');
}

// Tab1: 기존 페르소나 파이프라인
async function runTab1Pipeline() {
    const btn = document.getElementById('tab1-run-btn');
    const errorDiv = document.getElementById('tab1-error');
    const resultsDiv = document.getElementById('tab1-results');
    
    const youtubeUrl = document.getElementById('tab1-youtube-url').value.trim();
    const topic = document.getElementById('tab1-topic').value.trim();
    const rounds = parseInt(document.getElementById('tab1-rounds').value);
    
    if (!youtubeUrl) {
        showError(errorDiv, 'YouTube URL을 입력하세요');
        return;
    }
    
    // UI 상태 변경
    btn.disabled = true;
    btn.querySelector('.btn-text').textContent = '처리 중...';
    btn.querySelector('.spinner').style.display = 'inline-block';
    errorDiv.classList.remove('show');
    resultsDiv.classList.remove('show');
    
    try {
        const response = await fetch('/api/tab1/youtube-pipeline', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                youtube_url: youtubeUrl,
                topic: topic,
                rounds: rounds
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || '처리 실패');
        }
        
        // 결과 표시
        displayTab1Results(data);
        resultsDiv.classList.add('show');
        
    } catch (error) {
        showError(errorDiv, error.message);
    } finally {
        btn.disabled = false;
        btn.querySelector('.btn-text').textContent = 'YouTube 분석 및 AI 토론 시작';
        btn.querySelector('.spinner').style.display = 'none';
    }
}

function displayTab1Results(data) {
    // 통계 표시
    const statsDiv = document.getElementById('tab1-stats');
    statsDiv.innerHTML = `
        <div class="stat-card">
            <div class="stat-label">좌파 댓글</div>
            <div class="stat-value" style="color: #2196f3;">${data.classification.left_count}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">우파 댓글</div>
            <div class="stat-value" style="color: #f44336;">${data.classification.right_count}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">총 댓글</div>
            <div class="stat-value">${data.classification.total}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">토론 라운드</div>
            <div class="stat-value">${data.debate.length / 2}</div>
        </div>
    `;
    
    // 토론 표시
    const debateDiv = document.getElementById('tab1-debate');
    debateDiv.innerHTML = '';
    
    data.debate.forEach(msg => {
        const msgDiv = document.createElement('div');
        msgDiv.className = `debate-message ${msg.speaker === '좌파' ? 'left' : 'right'}`;
        msgDiv.innerHTML = `
            <div class="debate-speaker ${msg.speaker === '좌파' ? 'left' : 'right'}">
                ${msg.speaker === '좌파' ? '🔴' : '🔵'} ${msg.speaker} (라운드 ${msg.round})
            </div>
            <div class="debate-text">${msg.message}</div>
        `;
        debateDiv.appendChild(msgDiv);
    });
}

// Tab1: 팩트체크
async function runTab1Factcheck() {
    const claim = document.getElementById('tab1-factcheck-claim').value.trim();
    const resultDiv = document.getElementById('tab1-factcheck-result');
    
    if (!claim) {
        alert('팩트체크할 주장을 입력하세요');
        return;
    }
    
    resultDiv.innerHTML = '<p>⏳ 팩트체크 진행 중...</p>';
    
    try {
        const response = await fetch('/api/tab1/factcheck', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ claim: claim })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || '팩트체크 실패');
        }
        
        displayFactcheckResult(resultDiv, data.result);
        
    } catch (error) {
        resultDiv.innerHTML = `<p style="color: red;">오류: ${error.message}</p>`;
    }
}

// Tab2: LoRA 페르소나 파이프라인
async function runTab2Pipeline() {
    const btn = document.getElementById('tab2-run-btn');
    const errorDiv = document.getElementById('tab2-error');
    const resultsDiv = document.getElementById('tab2-results');
    
    const youtubeUrl = document.getElementById('tab2-youtube-url').value.trim();
    const topic = document.getElementById('tab2-topic').value.trim();
    const rounds = parseInt(document.getElementById('tab2-rounds').value);
    
    if (!youtubeUrl) {
        showError(errorDiv, 'YouTube URL을 입력하세요');
        return;
    }
    
    // UI 상태 변경
    btn.disabled = true;
    btn.querySelector('.btn-text').textContent = '처리 중...';
    btn.querySelector('.spinner').style.display = 'inline-block';
    errorDiv.classList.remove('show');
    resultsDiv.classList.remove('show');
    
    try {
        const response = await fetch('/api/tab2/youtube-pipeline', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                youtube_url: youtubeUrl,
                topic: topic,
                rounds: rounds,
                train_model: false  // Mock 모드
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || '처리 실패');
        }
        
        // 결과 표시
        displayTab2Results(data);
        resultsDiv.classList.add('show');
        
    } catch (error) {
        showError(errorDiv, error.message);
    } finally {
        btn.disabled = false;
        btn.querySelector('.btn-text').textContent = 'YouTube 분석 및 AI 토론 시작';
        btn.querySelector('.spinner').style.display = 'none';
    }
}

function displayTab2Results(data) {
    // 통계 표시
    const statsDiv = document.getElementById('tab2-stats');
    statsDiv.innerHTML = `
        <div class="stat-card">
            <div class="stat-label">좌파 댓글</div>
            <div class="stat-value" style="color: #2196f3;">${data.classification.left_count}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">우파 댓글</div>
            <div class="stat-value" style="color: #f44336;">${data.classification.right_count}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">총 댓글</div>
            <div class="stat-value">${data.classification.total}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">토론 라운드</div>
            <div class="stat-value">${data.debate.length / 2}</div>
        </div>
    `;
    
    // MAE 분석 표시
    const maeDiv = document.getElementById('tab2-mae');
    if (data.mae_analysis) {
        maeDiv.innerHTML = `
            <div class="stat-card">
                <div class="stat-label">좌파 공격성</div>
                <div class="stat-value" style="color: #2196f3;">
                    ${(data.mae_analysis.left.style_summary.aggression_level * 100).toFixed(0)}%
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-label">우파 공격성</div>
                <div class="stat-value" style="color: #f44336;">
                    ${(data.mae_analysis.right.style_summary.aggression_level * 100).toFixed(0)}%
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-label">좌파 학습 데이터</div>
                <div class="stat-value">${data.mae_analysis.left.training_texts_count}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">우파 학습 데이터</div>
                <div class="stat-value">${data.mae_analysis.right.training_texts_count}</div>
            </div>
        `;
    }
    
    // 토론 표시
    const debateDiv = document.getElementById('tab2-debate');
    debateDiv.innerHTML = '';
    
    data.debate.forEach(msg => {
        const msgDiv = document.createElement('div');
        msgDiv.className = `debate-message ${msg.speaker === '좌파' ? 'left' : 'right'}`;
        msgDiv.innerHTML = `
            <div class="debate-speaker ${msg.speaker === '좌파' ? 'left' : 'right'}">
                ${msg.speaker === '좌파' ? '🔴' : '🔵'} ${msg.speaker} (라운드 ${msg.round})
            </div>
            <div class="debate-text">${msg.message}</div>
        `;
        debateDiv.appendChild(msgDiv);
    });
}

// Tab2: 팩트체크
async function runTab2Factcheck() {
    const claim = document.getElementById('tab2-factcheck-claim').value.trim();
    const resultDiv = document.getElementById('tab2-factcheck-result');
    
    if (!claim) {
        alert('팩트체크할 주장을 입력하세요');
        return;
    }
    
    resultDiv.innerHTML = '<p>⏳ 팩트체크 진행 중...</p>';
    
    try {
        const response = await fetch('/api/tab2/factcheck', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ claim: claim })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || '팩트체크 실패');
        }
        
        displayFactcheckResult(resultDiv, data.result);
        
    } catch (error) {
        resultDiv.innerHTML = `<p style="color: red;">오류: ${error.message}</p>`;
    }
}

// 팩트체크 결과 표시
function displayFactcheckResult(container, result) {
    const verdictClass = result.verdict.toLowerCase();
    const verdictEmoji = {
        'true': '✅',
        'false': '❌',
        'uncertain': '❓'
    }[verdictClass] || '❓';
    
    let html = `
        <div class="factcheck-result">
            <div class="verdict ${verdictClass}">
                ${verdictEmoji} 판정: ${result.verdict}
            </div>
            <p><strong>신뢰도:</strong> ${result.confidence_score.toFixed(1)}/10</p>
            <p><strong>주장:</strong> ${result.claim}</p>
    `;
    
    if (result.evidences && result.evidences.length > 0) {
        html += '<div class="evidence-list"><h4>증거:</h4>';
        result.evidences.forEach((evidence, idx) => {
            html += `
                <div class="evidence-item">
                    <div class="evidence-title">${idx + 1}. ${evidence.title}</div>
                    <div class="evidence-source">${evidence.source} | 관련도: ${(evidence.relevance * 100).toFixed(0)}%</div>
                </div>
            `;
        });
        html += '</div>';
    }
    
    html += '</div>';
    container.innerHTML = html;
}

// 에러 표시
function showError(errorDiv, message) {
    errorDiv.textContent = `오류: ${message}`;
    errorDiv.classList.add('show');
}

