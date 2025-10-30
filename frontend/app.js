// ColorWar API 클라이언트

const API_BASE = window.location.origin;

// ==================== YouTube 파이프라인 ====================
async function runYoutubePipeline() {
    const url = document.getElementById('youtube-url').value;
    const topic = document.getElementById('youtube-topic').value;
    
    if (!url) {
        alert('YouTube URL을 입력해주세요');
        return;
    }
    
    const loading = document.getElementById('youtube-loading');
    const result = document.getElementById('youtube-result');
    const resultContent = document.getElementById('youtube-result-content');
    
    try {
        loading.classList.add('show');
        result.classList.remove('show');
        
        const response = await fetch(`${API_BASE}/api/structure/youtube-pipeline`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                youtube_url: url,
                topic: topic,
                rounds: 5
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || '처리 실패');
        }
        
        // 결과 표시
        resultContent.textContent = formatYoutubeResult(data);
        result.classList.add('show');
        
    } catch (error) {
        alert(`오류 발생: ${error.message}`);
    } finally {
        loading.classList.remove('show');
    }
}

function formatYoutubeResult(data) {
    let text = '';
    
    text += `✅ 처리 완료!\n\n`;
    text += `📹 비디오 ID: ${data.video_id}\n\n`;
    
    if (data.summary) {
        text += `📝 요약:\n${JSON.stringify(data.summary, null, 2)}\n\n`;
    }
    
    if (data.analysis && data.analysis.statistics) {
        text += `📊 댓글 분석:\n`;
        text += `  좌파: ${data.analysis.statistics.left_count || 0}개\n`;
        text += `  우파: ${data.analysis.statistics.right_count || 0}개\n`;
        text += `  전체: ${data.analysis.statistics.total || 0}개\n\n`;
    }
    
    if (data.debate && data.debate.length > 0) {
        text += `🎭 토론 결과: ${data.debate.length}개 메시지\n`;
    }
    
    // YouTube 결과를 Persona로 자동 전달
    if (data.analysis && data.analysis.left_comments && data.analysis.right_comments) {
        text += `\n\n🔄 AI 페르소나로 데이터 전송 중...\n`;
        autoSendToPersona(data.analysis.left_comments, data.analysis.right_comments);
    }
    
    return text;
}

// YouTube 결과를 자동으로 Persona에 전달
async function autoSendToPersona(leftComments, rightComments) {
    try {
        // 좌파 댓글 textarea에 채우기
        const leftTextarea = document.getElementById('left-comments');
        const rightTextarea = document.getElementById('right-comments');
        
        if (leftTextarea && leftComments && leftComments.length > 0) {
            leftTextarea.value = leftComments.slice(0, 20).join('\n');
        }
        
        if (rightTextarea && rightComments && rightComments.length > 0) {
            rightTextarea.value = rightComments.slice(0, 20).join('\n');
        }
        
        // 페르소나 결과 영역에 알림 표시
        const personaResult = document.getElementById('persona-result');
        const personaResultContent = document.getElementById('persona-result-content');
        
        if (personaResult && personaResultContent) {
            personaResultContent.textContent = `✅ YouTube 댓글 데이터가 자동으로 입력되었습니다!\n\n좌파 댓글: ${leftComments.length}개\n우파 댓글: ${rightComments.length}개\n\n👇 아래 '페르소나 생성' 버튼을 눌러주세요.`;
            personaResult.classList.add('show');
            
            // 페르소나 카드로 스크롤
            document.querySelector('.module-card:nth-child(2)').scrollIntoView({ 
                behavior: 'smooth', 
                block: 'center' 
            });
        }
    } catch (error) {
        console.error('Persona 데이터 전송 실패:', error);
    }
}

// ==================== AI 페르소나 ====================
async function generatePersona() {
    const leftText = document.getElementById('left-comments').value;
    const rightText = document.getElementById('right-comments').value;
    
    const leftComments = leftText.split('\n').filter(c => c.trim());
    const rightComments = rightText.split('\n').filter(c => c.trim());
    
    if (leftComments.length < 1 || rightComments.length < 1) {
        alert('좌파와 우파 댓글을 각각 1개 이상 입력해주세요');
        return;
    }
    
    const loading = document.getElementById('persona-loading');
    const result = document.getElementById('persona-result');
    const resultContent = document.getElementById('persona-result-content');
    
    try {
        loading.classList.add('show');
        result.classList.remove('show');
        
        // 1. 좌파 댓글 등록
        for (const comment of leftComments) {
            await fetch(`${API_BASE}/api/persona/api/comments/left`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    comment_text: comment
                })
            });
        }
        
        // 2. 우파 댓글 등록
        for (const comment of rightComments) {
            await fetch(`${API_BASE}/api/persona/api/comments/right`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    comment_text: comment
                })
            });
        }
        
        // 3. 페르소나 생성
        const response = await fetch(`${API_BASE}/api/persona/api/comments/generate-persona`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || '페르소나 생성 실패');
        }
        
        // 결과 표시
        resultContent.textContent = formatPersonaResult(data);
        result.classList.add('show');
        
    } catch (error) {
        alert(`오류 발생: ${error.message}`);
    } finally {
        loading.classList.remove('show');
    }
}

function formatPersonaResult(data) {
    let text = '';
    
    text += `✅ 페르소나 생성 완료!\n\n`;
    
    if (data.left_persona) {
        text += `👈 좌파 페르소나:\n`;
        text += `${JSON.stringify(data.left_persona, null, 2)}\n\n`;
    }
    
    if (data.right_persona) {
        text += `👉 우파 페르소나:\n`;
        text += `${JSON.stringify(data.right_persona, null, 2)}\n\n`;
    }
    
    text += `\n💡 이제 토론을 시작할 수 있습니다!\n`;
    text += `API: POST /api/persona/api/debate/start\n`;
    
    return text;
}

// ==================== 팩트체크 ====================
async function runFactcheck() {
    const claim = document.getElementById('factcheck-claim').value;
    
    if (!claim) {
        alert('검증할 주장을 입력해주세요');
        return;
    }
    
    const loading = document.getElementById('factcheck-loading');
    const result = document.getElementById('factcheck-result');
    const resultContent = document.getElementById('factcheck-result-content');
    
    try {
        loading.classList.add('show');
        result.classList.remove('show');
        
        const response = await fetch(`${API_BASE}/api/factcheck/factcheck`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                claim: claim
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || '팩트체크 실패');
        }
        
        // 결과 표시
        resultContent.textContent = formatFactcheckResult(data);
        result.classList.add('show');
        
    } catch (error) {
        alert(`오류 발생: ${error.message}`);
    } finally {
        loading.classList.remove('show');
    }
}

function formatFactcheckResult(data) {
    let text = '';
    
    text += `📋 주장: ${data.claim}\n\n`;
    
    const verdictEmoji = {
        'True': '✅',
        'False': '❌',
        'Uncertain': '❓'
    };
    
    text += `${verdictEmoji[data.verdict] || '?'} 판정: ${data.verdict}\n`;
    text += `⭐ 신뢰도: ${data.confidence_score}/10 (${data.confidence_level})\n\n`;
    
    text += `💡 판정 근거:\n${data.reasoning}\n\n`;
    
    if (data.evidences && data.evidences.length > 0) {
        text += `📚 참고 증거 (${data.evidences.length}개):\n\n`;
        data.evidences.forEach((ev, idx) => {
            text += `[${idx + 1}] ${ev.source} (${ev.date})\n`;
            text += `    ${ev.text}\n`;
            text += `    관련도: ${ev.relevance}\n\n`;
        });
    }
    
    if (data.score_breakdown) {
        text += `📊 신뢰도 세부:\n`;
        for (const [key, value] of Object.entries(data.score_breakdown)) {
            text += `  - ${key}: ${value}\n`;
        }
    }
    
    return text;
}

