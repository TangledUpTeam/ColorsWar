// ColorWar API 클라이언트

const API_BASE = window.location.origin;

// ==================== YouTube 파이프라인 ====================
function normalizeYouTubeUrl(inputUrl) {
    try {
        const u = new URL(inputUrl);
        // youtu.be short link → watch?v=
        if (u.hostname === 'youtu.be') {
            const id = u.pathname.slice(1);
            if (id) return `https://www.youtube.com/watch?v=${id}`;
        }
        // shorts → watch?v=
        if (u.hostname.includes('youtube.com') && u.pathname.startsWith('/shorts/')) {
            const id = u.pathname.split('/')[2];
            if (id) return `https://www.youtube.com/watch?v=${id}`;
        }
        return inputUrl;
    } catch (e) {
        return inputUrl;
    }
}

async function runYoutubePipeline() {
    const rawUrl = document.getElementById('youtube-url').value;
    const topic = document.getElementById('youtube-topic').value;
    
    if (!rawUrl) {
        alert('YouTube URL을 입력해주세요');
        return;
    }
    const url = normalizeYouTubeUrl(rawUrl);
    
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
    
    // <br> 태그를 실제 줄바꿈으로 변환
    const leftComments = leftText.replace(/<br\s*\/?>/gi, '\n').split('\n').filter(c => c.trim());
    const rightComments = rightText.replace(/<br\s*\/?>/gi, '\n').split('\n').filter(c => c.trim());
    
    console.log('📊 전송할 댓글 수:', { left: leftComments.length, right: rightComments.length });
    console.log('📝 좌파 댓글 샘플:', leftComments.slice(0, 3));
    console.log('📝 우파 댓글 샘플:', rightComments.slice(0, 3));
    
    if (leftComments.length < 5 || rightComments.length < 5) {
        alert(`좌파와 우파 댓글을 각각 5개 이상 입력해주세요\n현재: 좌파 ${leftComments.length}개, 우파 ${rightComments.length}개`);
        return;
    }
    
    const loading = document.getElementById('persona-loading');
    const result = document.getElementById('persona-result');
    const resultContent = document.getElementById('persona-result-content');
    
    try {
        loading.classList.add('show');
        result.classList.remove('show');
        
        // 1. 좌파/우파 댓글 배치 등록 (백엔드 스키마: { comments: string[] })
        console.log('🚀 좌파 댓글 전송 중...');
        const leftRes = await fetch(`${API_BASE}/api/persona/api/comments/left`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ comments: leftComments })
        });

        if (!leftRes.ok) {
            const err = await leftRes.json().catch(() => ({}));
            console.error('❌ 좌파 댓글 등록 실패:', err);
            throw new Error(err.detail || '좌파 댓글 등록 실패');
        }
        const leftData = await leftRes.json();
        console.log('✅ 좌파 댓글 등록 성공:', leftData);
        
        console.log('🚀 우파 댓글 전송 중...');
        const rightRes = await fetch(`${API_BASE}/api/persona/api/comments/right`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ comments: rightComments })
        });
        
        if (!rightRes.ok) {
            const err = await rightRes.json().catch(() => ({}));
            console.error('❌ 우파 댓글 등록 실패:', err);
            throw new Error(err.detail || '우파 댓글 등록 실패');
        }
        const rightData = await rightRes.json();
        console.log('✅ 우파 댓글 등록 성공:', rightData);
         
        // 2. 페르소나 생성
        console.log('🚀 페르소나 생성 요청 중...');
        const response = await fetch(`${API_BASE}/api/persona/api/comments/generate-persona`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            console.error('❌ 페르소나 생성 실패:', data);
            throw new Error(data.detail || '페르소나 생성 실패');
        }
        
        console.log('✅ 페르소나 생성 성공!');
        
        // 페르소나 정보를 먼저 표시
        let personaInfo = formatPersonaResult(data);
        resultContent.textContent = personaInfo + '\n\n🚀 토론을 시작합니다...\n';
        result.classList.add('show');
        
        // 3. 자동으로 토론 시작
        console.log('🚀 토론 시작 요청 중...');
        const debateStartRes = await fetch(`${API_BASE}/api/persona/api/debate/start`, {
            method: 'POST'
        });
        
        if (!debateStartRes.ok) {
            const err = await debateStartRes.json().catch(() => ({}));
            console.error('⚠️ 토론 시작 실패:', err);
            resultContent.textContent = personaInfo + '\n\n⚠️ 페르소나는 생성되었으나 토론 시작에 실패했습니다.\n' + (err.detail || '');
            return;
        }
        
        const debateData = await debateStartRes.json();
        console.log('✅ 토론 시작 성공!');
        
        // 4. 토론 메시지들을 생성 (최대 10개)
        resultContent.textContent = personaInfo + '\n\n💬 토론 진행 중...\n\n';
        
        for (let i = 0; i < 10; i++) {
            try {
                const nextRes = await fetch(`${API_BASE}/api/persona/api/debate/next`, {
                    method: 'POST'
                });
                
                if (!nextRes.ok) {
                    console.log('토론 종료 또는 오류');
                    break;
                }
                
                const nextData = await nextRes.json();
                const message = nextData.message;
                
                // 토론 메시지를 누적해서 표시
                const sideEmoji = message.side === 'left' ? '👈' : '👉';
                const sideName = message.side === 'left' ? '좌파' : '우파';
                resultContent.textContent += `${sideEmoji} ${sideName}: ${message.content}\n\n`;
                
                // 스크롤을 결과 영역으로 이동
                result.scrollTop = result.scrollHeight;
                
                // 약간의 딜레이 (너무 빠르면 읽기 힘듦)
                await new Promise(resolve => setTimeout(resolve, 500));
                
            } catch (err) {
                console.error('토론 메시지 생성 오류:', err);
                break;
            }
        }
        
        resultContent.textContent += '\n✅ 토론이 완료되었습니다!';
        console.log('✅ 토론 완료!');
        
    } catch (error) {
        console.error('❌ 오류:', error);
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
        const lp = data.left_persona;
        text += `  📝 요약: ${lp.summary || 'N/A'}\n`;
        text += `  💎 가치관: ${(lp.values || []).join(', ')}\n`;
        text += `  🗣️ 말투: ${(lp.tone || []).join(', ')}\n`;
        text += `  😊 감정: ${lp.emotion || 'N/A'}\n`;
        text += `  🔑 키워드: ${(lp.keywords || []).slice(0, 5).join(', ')}\n\n`;
    }
    
    if (data.right_persona) {
        text += `👉 우파 페르소나:\n`;
        const rp = data.right_persona;
        text += `  📝 요약: ${rp.summary || 'N/A'}\n`;
        text += `  💎 가치관: ${(rp.values || []).join(', ')}\n`;
        text += `  🗣️ 말투: ${(rp.tone || []).join(', ')}\n`;
        text += `  😊 감정: ${rp.emotion || 'N/A'}\n`;
        text += `  🔑 키워드: ${(rp.keywords || []).slice(0, 5).join(', ')}\n\n`;
    }
    
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

