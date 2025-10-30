/**
 * AI 페르소나 배틀 시스템 JavaScript - YouTube 파이프라인 전용
 */

// DOM 요소
const youtubeUrlInput = document.getElementById('youtubeUrl');
const youtubeTopicInput = document.getElementById('youtubeTopic');
const debateRoundsInput = document.getElementById('debateRounds');
const processYoutubeBtn = document.getElementById('processYoutubeBtn');
const errorMessage = document.getElementById('errorMessage');

const trainingSection = document.getElementById('trainingSection');
const leftCount = document.getElementById('leftCount');
const rightCount = document.getElementById('rightCount');

const youtubeProgress = document.getElementById('youtubeProgress');
const youtubeSteps = document.getElementById('youtubeSteps');
const youtubeResult = document.getElementById('youtubeResult');
const youtubeSummary = document.getElementById('youtubeSummary');
const youtubeAnalysis = document.getElementById('youtubeAnalysis');
const youtubeDebate = document.getElementById('youtubeDebate');

/**
 * YouTube 파이프라인 처리
 */
processYoutubeBtn.addEventListener('click', async () => {
    const youtubeUrl = youtubeUrlInput.value.trim();
    const topic = youtubeTopicInput.value.trim() || '현재 정부 정책';
    const rounds = parseInt(debateRoundsInput.value) || 5;
    
    if (!youtubeUrl) {
        showError('YouTube URL을 입력해주세요.');
        return;
    }
    
    try {
        setLoading(processYoutubeBtn, true);
        hideError();
        
        // 진행 상황 표시
        showYoutubeProgress();
        
        const response = await fetch('/api/youtube-pipeline', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                youtube_url: youtubeUrl,
                topic: topic,
                rounds: rounds
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'YouTube 처리에 실패했습니다.');
        }
        
        const result = await response.json();
        displayYoutubeResult(result);
        
        // 학습 데이터 업데이트
        updateTrainingStats();
        
    } catch (error) {
        console.error('YouTube 처리 오류:', error);
        showError('YouTube 처리 중 오류가 발생했습니다: ' + error.message);
    } finally {
        setLoading(processYoutubeBtn, false);
        hideYoutubeProgress();
    }
});

/**
 * YouTube 진행 상황 표시
 */
function showYoutubeProgress() {
    youtubeProgress.style.display = 'block';
    youtubeSteps.innerHTML = `
        <div class="progress-step">🎵 오디오 다운로드 중...</div>
        <div class="progress-step">🎤 음성 전사 중...</div>
        <div class="progress-step">📝 요약 추출 중...</div>
        <div class="progress-step">💬 댓글 수집 중...</div>
        <div class="progress-step">🔍 댓글 분석 중...</div>
        <div class="progress-step">🎭 AI 토론 중...</div>
    `;
}

/**
 * YouTube 진행 상황 숨기기
 */
function hideYoutubeProgress() {
    youtubeProgress.style.display = 'none';
}

/**
 * YouTube 결과 표시
 */
function displayYoutubeResult(result) {
    youtubeResult.style.display = 'block';
    
    // 요약 표시
    youtubeSummary.innerHTML = `
        <div class="result-section">
            <h4>📝 영상 요약</h4>
            <div class="summary-content">
                <p><strong>개요:</strong> ${result.summary.overview || 'N/A'}</p>
                <p><strong>핵심 발언:</strong> ${result.summary.sayings || 'N/A'}</p>
                <p><strong>배경:</strong> ${result.summary.context || 'N/A'}</p>
                <p><strong>결과:</strong> ${result.summary.result || 'N/A'}</p>
            </div>
        </div>
    `;
    
    // 댓글 분석 표시
    youtubeAnalysis.innerHTML = `
        <div class="result-section">
            <h4>📊 댓글 분석 결과</h4>
            <div class="analysis-stats">
                ${Object.entries(result.analysis.statistics).map(([orientation, stats]) => `
                    <div class="stat-item ${orientation.toLowerCase()}">
                        <span class="orientation">${orientation}</span>
                        <span class="count">${stats.count}개</span>
                        <span class="percentage">${stats.percentage}%</span>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
    
    // 토론 결과 표시
    if (result.debate && result.debate.length > 0) {
        youtubeDebate.innerHTML = `
            <div class="result-section">
                <h4>🎭 AI 페르소나 토론</h4>
                <div class="debate-messages">
                    ${result.debate.map((msg, index) => `
                        <div class="debate-message ${msg.speaker === '좌파' ? 'left' : 'right'}">
                            <div class="debate-speaker">${msg.speaker} (R${msg.round})</div>
                            <div class="debate-content">${msg.message}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    } else {
        youtubeDebate.innerHTML = `
            <div class="result-section">
                <h4>🎭 AI 페르소나 토론</h4>
                <p>토론을 시작할 수 없습니다. 좌파 또는 우파 댓글이 부족합니다.</p>
            </div>
        `;
    }
}

/**
 * 학습 데이터 통계 업데이트
 */
async function updateTrainingStats() {
    try {
        const response = await fetch('/api/battle/training-data');
        if (response.ok) {
            const data = await response.json();
            leftCount.textContent = data.left.count;
            rightCount.textContent = data.right.count;
            trainingSection.style.display = 'block';
        }
    } catch (error) {
        console.error('학습 데이터 업데이트 오류:', error);
    }
}

/**
 * 버튼 로딩 상태
 */
function setLoading(button, isLoading) {
    const textSpan = button.querySelector('.btn-text');
    const spinner = button.querySelector('.spinner');
    
    if (isLoading) {
        button.disabled = true;
        textSpan.textContent = '처리 중...';
        spinner.style.display = 'inline-block';
    } else {
        button.disabled = false;
        textSpan.textContent = 'YouTube 분석 및 AI 토론 시작';
        spinner.style.display = 'none';
    }
}

/**
 * 에러 메시지 표시
 */
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
}

/**
 * 에러 메시지 숨기기
 */
function hideError() {
    errorMessage.style.display = 'none';
}

/**
 * HTML 이스케이프
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 페이지 로드 시 학습 데이터 업데이트
document.addEventListener('DOMContentLoaded', () => {
    updateTrainingStats();
});