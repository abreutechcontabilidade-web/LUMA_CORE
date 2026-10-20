import zlib, base64, os, json

BLOCOS = {
    "CANVAS": "const canvas=document.getElementById('game');const ctx=canvas.getContext('2d');",
    "LOOP": "function update(t=0){draw();requestAnimationFrame(update);}",
    "STYLE": "<style>body{background:#050510;color:#00ffe1;font-family:monospace;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;}canvas{border:2px solid #00ffe1;box-shadow:0 0 20px #00ffe1;}</style>",
    
    # --- FLAPPY BIRD ---
    "PHYS_FLAPPY": "let bird={x:100,y:250,vy:0,w:30,h:20};let pipes=[];let score=0;let gameOver=false;let frames=0;",
    "DRAW_FLAPPY": """
        ctx.fillStyle='#0a0a1a';ctx.fillRect(0,0,800,500);
        if(gameOver){ctx.fillStyle='#fff';ctx.font='40px monospace';ctx.fillText('GAME OVER',250,250);return;}
        ctx.fillStyle='#00ffe1';ctx.fillRect(bird.x,bird.y,bird.w,bird.h);
        bird.vy+=0.5; bird.y+=bird.vy;
        if(bird.y>500||bird.y<0) gameOver=true;
        if(frames%120===0) pipes.push({x:800,y:Math.random()*300+100,w:80,h:250,passed:false});
        pipes.forEach(p=>{
            ctx.fillStyle='#ff2fd6'; ctx.fillRect(p.x,p.y,p.w,500);
            p.x-=4;
            if(bird.x+bird.w>p.x && bird.x<p.x+p.w && (bird.y<p.y || bird.y+bird.h>p.y+250)) gameOver=true;
            if(!p.passed && p.x+p.w<bird.x){ p.passed=true; score++; }
        });
        pipes=pipes.filter(p=>p.x>-100);
        ctx.fillStyle='#fff'; ctx.font='30px monospace'; ctx.fillText('SCORE: '+score, 20, 40);
        frames++;
    """,
    "INPUT_FLAPPY": "addEventListener('keydown',e=>{if(e.key===' '&&!gameOver) bird.vy=-8; if(gameOver&&e.key===' '){bird.y=250;bird.vy=0;pipes=[];score=0;gameOver=false;}});",

    # --- ASTEROIDS ---
    "PHYS_ASTEROIDS": "let ship={x:400,y:300,angle:0,vx:0,vy:0};let bullets=[];let asteroids=[];let score=0;",
    "DRAW_ASTEROIDS": """
        ctx.fillStyle='#0a0a1a';ctx.fillRect(0,0,800,500);
        ctx.save(); ctx.translate(ship.x,ship.y); ctx.rotate(ship.angle);
        ctx.strokeStyle='#00ffe1'; ctx.lineWidth=2; ctx.beginPath();
        ctx.moveTo(15,0); ctx.lineTo(-10,-10); ctx.lineTo(-5,0); ctx.lineTo(-10,10); ctx.closePath(); ctx.stroke(); ctx.restore();
        ship.x+=ship.vx; ship.y+=ship.vy; ship.vx*=0.98; ship.vy*=0.98;
        if(ship.x<0)ship.x=800; if(ship.x>800)ship.x=0; if(ship.y<0)ship.y=500; if(ship.y>500)ship.y=0;
        ctx.fillStyle='#fff'; bullets.forEach(b=>{ctx.beginPath();ctx.arc(b.x,b.y,3,0,Math.PI*2);ctx.fill(); b.x+=b.vx; b.y+=b.vy;});
        bullets=bullets.filter(b=>b.x>0&&b.x<800&&b.y>0&&b.y<500);
        if(frames%100===0) asteroids.push({x:Math.random()*800,y:Math.random()*500,r:20+Math.random()*20,vx:(Math.random()-0.5)*2,vy:(Math.random()-0.5)*2});
        ctx.strokeStyle='#ff2fd6'; asteroids.forEach(a=>{ctx.beginPath();ctx.arc(a.x,a.y,a.r,0,Math.PI*2);ctx.stroke(); a.x+=a.vx; a.y+=a.vy;});
        asteroids.forEach(a=>{ bullets.forEach(b=>{ if(Math.hypot(a.x-b.x,a.y-b.y)<a.r){ a.dead=true; b.dead=true; score+=10; } }); });
        asteroids=asteroids.filter(a=>!a.dead); bullets=bullets.filter(b=>!b.dead);
        ctx.fillStyle='#fff'; ctx.font='30px monospace'; ctx.fillText('SCORE: '+score, 20, 40);
        frames++;
    """,
    "INPUT_ASTEROIDS": "addEventListener('keydown',e=>{if(e.key==='ArrowLeft')ship.angle-=0.2; if(e.key==='ArrowRight')ship.angle+=0.2; if(e.key==='ArrowUp'){ship.vx+=Math.cos(ship.angle-1.57)*0.5;ship.vy+=Math.sin(ship.angle-1.57)*0.5;} if(e.key===' '){bullets.push({x:ship.x,y:ship.y,vx:Math.cos(ship.angle-1.57)*10,vy:Math.sin(ship.angle-1.57)*10});}});",

    # --- JOGO DA FORCA ---
    "PHYS_FORCA": "let palavra='CYBERPUNK';let letras=[];let erros=0;let maxErros=6;let ganhou=false;",
    "DRAW_FORCA": """
        ctx.fillStyle='#0a0a1a';ctx.fillRect(0,0,800,500);
        ctx.fillStyle='#00ffe1'; ctx.font='30px monospace'; ctx.fillText('ERROS: '+erros+' / '+maxErros, 50, 50);
        
        ctx.fillStyle='#fff'; ctx.font='40px monospace';
        let display = palavra.split('').map(l => letras.includes(l) ? l : '_').join(' ');
        ctx.fillText(display, 150, 250);
        
        if (erros >= maxErros) { ctx.fillStyle='#ff2fd6'; ctx.fillText('VOCE PERDEU!', 200, 350); }
        else if (palavra.split('').every(l => letras.includes(l))) { ctx.fillStyle='#ff2fd6'; ctx.fillText('VOCE GANHOU!', 200, 350); }
    """,
    "INPUT_FORCA": "addEventListener('keydown',e=>{if(erros>=maxErros || palavra.split('').every(l=>letras.includes(l))) return; let l=e.key.toUpperCase(); if(l.length===1 && l>='A' && l<='Z'){ if(!letras.includes(l)){ letras.push(l); if(!palavra.includes(l)) erros++; } }});"
}

json_str = json.dumps(BLOCOS)
comprimido = zlib.compress(json_str.encode('utf-8'))
criptografado = base64.b64encode(comprimido)

caminho = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\genoma_cripto.bin"
with open(caminho, "wb") as f: f.write(criptografado)
print(f"[OK] Genoma expandido (Flappy+Asteroids+Forca): {len(criptografado)} bytes.")
