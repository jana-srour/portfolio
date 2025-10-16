const canvas = document.createElement('canvas');
document.body.prepend(canvas);
canvas.style.position='fixed';
canvas.style.top=0;
canvas.style.left=0;
canvas.style.width='100%';
canvas.style.height='100%';
canvas.style.zIndex=0;
canvas.style.pointerEvents='none';
const ctx = canvas.getContext('2d');
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

let particles = [];
for(let i=0;i<100;i++){
  particles.push({x:Math.random()*canvas.width, y:Math.random()*canvas.height, r:Math.random()*2+1, vx:(Math.random()-0.5)*0.3, vy:(Math.random()-0.5)*0.3});
}

function animate(){
  ctx.clearRect(0,0,canvas.width,canvas.height);
  particles.forEach(p=>{
    ctx.beginPath();
    ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
    ctx.fillStyle='rgba(187,0,255,0.3)';
    ctx.fill();
    p.x+=p.vx; p.y+=p.vy;
    if(p.x<0||p.x>canvas.width)p.vx*=-1;
    if(p.y<0||p.y>canvas.height)p.vy*=-1;
  });
  requestAnimationFrame(animate);
}
animate();
window.addEventListener('resize',()=>{
  canvas.width=window.innerWidth;
  canvas.height=window.innerHeight;
});
