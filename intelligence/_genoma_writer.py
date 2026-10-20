import zlib, base64, os, json

BLOCOS = {
    "CANVAS": "const canvas=document.getElementById('game');const ctx=canvas.getContext('2d');",
    "LOOP": "function update(t=0){draw();requestAnimationFrame(update);}",
    "STYLE": "<style>body{background:#050510;color:#00ffe1;font-family:monospace;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;}canvas{border:2px solid #00ffe1;box-shadow:0 0 20px #00ffe1;}</style>",
    
    # Física Pong com IA
    "PHYS_PONG_IA": "let p1={x:10,y:200},p2={x:780,y:200},ball={x:400,y:250,dx:5,dy:5};let score1=0,score2=0;",
    "DRAW_PONG_IA": """
        ctx.fillStyle='#0a0a1a';ctx.fillRect(0,0,800,500);
        ctx.fillStyle='#00ffe1';ctx.fillRect(p1.x,p1.y,10,80);
        ctx.fillStyle='#ff2fd6';ctx.fillRect(p2.x,p2.y,10,80);
        ctx.fillStyle='#fff';ctx.beginPath();ctx.arc(ball.x,ball.y,8,0,Math.PI*2);ctx.fill();
        ctx.fillStyle='#00ffe1';ctx.font='30px monospace';ctx.fillText(score1, 200, 50);
        ctx.fillStyle='#ff2fd6';ctx.fillText(score2, 600, 50);
        ball.x+=ball.dx; ball.y+=ball.dy;
        if(ball.y>492||ball.y<8) ball.dy*=-1;
        if(ball.x<20&&ball.y>p1.y&&ball.y<p1.y+80) ball.dx=Math.abs(ball.dx);
        if(ball.x>780&&ball.y>p2.y&&ball.y<p2.y+80) ball.dx=-Math.abs(ball.dx);
        if(ball.x>800){score1++;ball.x=400;ball.y=250;ball.dx=5;ball.dy=5;}
        if(ball.x<0){score2++;ball.x=400;ball.y=250;ball.dx=-5;ball.dy=5;}
        // IA P2
        if(ball.y > p2.y+40) p2.y += 5;
        if(ball.y < p2.y+40) p2.y -= 5;
    """,
    "INPUT_PONG_IA": "addEventListener('keydown',e=>{if(e.key==='w')p1.y-=10;if(e.key==='s')p1.y+=10;});",

    # Física Snake com IA
    "PHYS_SNAKE_IA": "let snake=[{x:10,y:10}];let vel={x:1,y:0};let apple={x:15,y:15};let score=0,speed=100,last=0,drop=0,gameOver=false;",
    "DRAW_SNAKE_IA": """
        ctx.fillStyle='#0a0a1a';ctx.fillRect(0,0,400,400);
        if(gameOver){ctx.fillStyle='#fff';ctx.font='30px monospace';ctx.fillText('GAME OVER',100,200);return;}
        snake.forEach((p,i)=>{ctx.fillStyle=i===0?'#fff':'#ff2fd6';ctx.fillRect(p.x*20,p.y*20,18,18);});
        ctx.fillStyle='#00ffe1';ctx.beginPath();ctx.arc(apple.x*20+10,apple.y*20+10,8,0,Math.PI*2);ctx.fill();
        // IA da Cobra
        let nextX = apple.x > snake[0].x ? 1 : (apple.x < snake[0].x ? -1 : 0);
        let nextY = apple.y > snake[0].y ? 1 : (apple.y < snake[0].y ? -1 : 0);
        if(nextX!==0) vel={x:nextX,y:0}; else vel={x:0,y:nextY};
        let head={x:snake[0].x+vel.x,y:snake[0].y+vel.y};
        if(head.x<0||head.x>=20||head.y<0||head.y>=20){gameOver=true;return;}
        snake.unshift(head);
        if(head.x===apple.x&&head.y===apple.y){score++;apple={x:Math.floor(Math.random()*20),y:Math.floor(Math.random()*20)};}
        else snake.pop();
    """,
    "INPUT_SNAKE_IA": "addEventListener('keydown',e=>{if(gameOver&&e.key===' '){snake=[{x:10,y:10}];gameOver=false;score=0;}});"
}

json_str = json.dumps(BLOCOS)
comprimido = zlib.compress(json_str.encode('utf-8'))
criptografado = base64.b64encode(comprimido)

caminho = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\genoma_cripto.bin"
with open(caminho, "wb") as f: f.write(criptografado)
print(f"[OK] Genoma de IA recompilado: {len(criptografado)} bytes.")
