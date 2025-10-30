/**
 * 댓글 분석 테스트 JavaScript (3~5단계 전용)
 */

// DOM 요소
const videoKeywordsInput = document.getElementById('videoKeywords');
const commentsInput = document.getElementById('commentsInput');
const analyzeBtn = document.getElementById('analyzeBtn');
const errorMessage = document.getElementById('errorMessage');

const step3Section = document.getElementById('step3Section');
const step3Stats = document.getElementById('step3Stats');
const step3Comments = document.getElementById('step3Comments');

const step4Section = document.getElementById('step4Section');
const step4Comments = document.getElementById('step4Comments');

const step5Section = document.getElementById('step5Section');
const step5Chart = document.getElementById('step5Chart');
const step5Comments = document.getElementById('step5Comments');

/**
 * 분석 시작
 */
analyzeBtn.addEventListener('click', async () => {
    // 입력값 가져오기
    const keywordsText = videoKeywordsInput.value.trim();
    const commentsText = commentsInput.value.trim();
    
    if (!keywordsText || !commentsText) {
        showError('키워드와 댓글을 모두 입력해주세요.');
        return;
    }
    
    // 데이터 파싱
    const keywords = keywordsText.split(',').map(k => k.trim()).filter(k => k);
    const comments = commentsText.split('\n').map(c => c.trim()).filter(c => c);
    
    if (keywords.length === 0) {
        showError('최소 1개 이상의 키워드를 입력해주세요.');
        return;
    }
    
    if (comments.length === 0) {
        showError('최소 1개 이상의 댓글을 입력해주세요.');
        return;
    }
    
    // UI 초기화
    hideError();
    step3Section.style.display = 'none';
    step4Section.style.display = 'none';
    step5Section.style.display = 'none';
    setButtonLoading(true);
    
    try {
        // API 호출
        const response = await fetch('/api/test/analyze-comments', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                keywords: keywords,
                comments: comments
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '분석 중 오류가 발생했습니다.');
        }
        
        const result = await response.json();
        
        // 결과 표시
        displayStep3(result.step3_filtered);
        displayStep4(result.step4_keywords);
        displayStep5(result.step5_classified);
        
        // 섹션 표시
        step3Section.style.display = 'block';
        step4Section.style.display = 'block';
        step5Section.style.display = 'block';
        
        // 스크롤
        step3Section.scrollIntoView({ behavior: 'smooth' });
        
    } catch (error) {
        showError(error.message);
        console.error('분석 오류:', error);
    } finally {
        setButtonLoading(false);
    }
});

/**
 * 3단계 결과 표시
 */
function displayStep3(data) {
    // 통계
    step3Stats.innerHTML = `
        <div class="stat-item">
            <div class="stat-label">전체 댓글</div>
            <div class="stat-value">${data.total_comments}</div>
        </div>
        <div class="stat-item">
            <div class="stat-label">필터링된 댓글</div>
            <div class="stat-value">${data.filtered_count}</div>
        </div>
        <div class="stat-item">
            <div class="stat-label">필터링 비율</div>
            <div class="stat-value">${data.filter_rate}%</div>
        </div>
    `;
    
    // 댓글 목록
    step3Comments.innerHTML = data.comments.map((comment, index) => `
        <div class="comment-item" style="background: #f0f8ff; border-left-color: #667eea;">
            <div class="comment-header">
                <span class="comment-author">댓글 #${index + 1}</span>
                <span style="font-size: 0.9rem; color: #666;">
                    매칭 키워드: ${comment.matched_keywords.length}개
                </span>
            </div>
            <div class="comment-text">${escapeHtml(comment.text)}</div>
            <div class="comment-keywords">
                ${comment.matched_keywords.map(kw => 
                    `<span class="keyword-tag" style="font-size: 0.85rem;">${escapeHtml(kw)}</span>`
                ).join('')}
            </div>
        </div>
    `).join('');
}

/**
 * 4단계 결과 표시
 */
function displayStep4(data) {
    step4Comments.innerHTML = data.comments.map((comment, index) => `
        <div class="comment-item" style="background: #fff8f0; border-left-color: #f5a623;">
            <div class="comment-header">
                <span class="comment-author">댓글 #${index + 1}</span>
                <span style="font-size: 0.9rem; color: #666;">
                    추출된 키워드: ${comment.keywords.length}개
                </span>
            </div>
            <div class="comment-text">${escapeHtml(comment.text)}</div>
            <div class="comment-keywords">
                ${comment.keywords.map(kw => 
                    `<span class="comment-keyword">${escapeHtml(kw)}</span>`
                ).join('')}
            </div>
        </div>
    `).join('');
}

/**
 * 5단계 결과 표시
 */
function displayStep5(data) {
    // 성향 분포 차트
    const orientations = [
        { key: '좌파', label: '좌파', class: 'fill-left' },
        { key: '우파', label: '우파', class: 'fill-right' },
        { key: '중도', label: '중도', class: 'fill-center' },
        { key: '판단불가', label: '판단불가', class: 'fill-unknown' }
    ];
    
    step5Chart.innerHTML = orientations.map(orientation => {
        const stat = data.statistics[orientation.key];
        return `
            <div class="chart-bar">
                <div class="chart-label">
                    <span>${orientation.label}</span>
                    <span>${stat.count}개 (${stat.percentage}%)</span>
                </div>
                <div class="chart-progress">
                    <div class="chart-fill ${orientation.class}" style="width: ${stat.percentage}%;">
                        ${stat.percentage > 10 ? stat.percentage + '%' : ''}
                    </div>
                </div>
            </div>
        `;
    }).join('');
    
    // 댓글 목록
    step5Comments.innerHTML = data.comments.map((comment, index) => {
        const orientation = comment.political_orientation || '판단불가';
        const orientationClass = getOrientationClass(orientation);
        
        return `
            <div class="comment-item ${orientationClass}">
                <div class="comment-header">
                    <span class="comment-author">댓글 #${index + 1}</span>
                    <span class="comment-orientation orientation-${orientationClass}">
                        ${orientation}
                    </span>
                </div>
                <div class="comment-text">${escapeHtml(comment.text)}</div>
                <div style="margin-top: 10px; padding: 10px; background: rgba(0,0,0,0.05); border-radius: 6px; font-size: 0.9rem;">
                    <strong>신뢰도:</strong> ${(comment.classification_confidence * 100).toFixed(1)}%<br>
                    <strong>근거:</strong> ${escapeHtml(comment.classification_reasoning)}
                </div>
                ${comment.keywords && comment.keywords.length > 0 ? `
                    <div class="comment-keywords" style="margin-top: 10px;">
                        ${comment.keywords.map(kw => 
                            `<span class="comment-keyword">${escapeHtml(kw)}</span>`
                        ).join('')}
                    </div>
                ` : ''}
            </div>
        `;
    }).join('');
}

/**
 * 성향 클래스 매핑
 */
function getOrientationClass(orientation) {
    const map = {
        '좌파': 'left',
        '우파': 'right',
        '중도': 'center',
        '판단불가': 'unknown'
    };
    return map[orientation] || 'unknown';
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
 * 버튼 로딩 상태
 */
function setButtonLoading(isLoading) {
    const textSpan = analyzeBtn.querySelector('.btn-text');
    const spinner = analyzeBtn.querySelector('.spinner');
    
    if (isLoading) {
        analyzeBtn.disabled = true;
        textSpan.textContent = '분석 중...';
        spinner.style.display = 'inline-block';
    } else {
        analyzeBtn.disabled = false;
        textSpan.textContent = '댓글 분석 시작 (3~5단계)';
        spinner.style.display = 'none';
    }
}

/**
 * HTML 이스케이프
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

