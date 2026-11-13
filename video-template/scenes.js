const SC={};const LIGHT=new Set(['check','protect','s1','win']);
function quoteCard(t,s,lines,ref,bg1,bg2,acc){bgFill(bg1,bg2);confetti(t,C.pink,0.25);const k=pop(t,s.start,0.5);g.save();g.translate(540,860);g.scale(k,k);
  const h=120+lines.length*80;rr(-440,-h/2-60,880,h+120,60,C.white);g.fillStyle=acc;g.font='600 140px Inter';g.textAlign='left';g.fillText('“',-400,-h/2+70);
  g.fillStyle=C.navy;g.font='600 54px Inter';g.textAlign='center';const per=(s.end-s.start-0.4)/lines.length;
  lines.forEach((l,i)=>{g.globalAlpha=prog(t,s.start+0.3+i*per,s.start+0.6+i*per);g.fillText(l,0,-h/2+110+i*80);});g.globalAlpha=1;g.restore();
  pill(ref,540,860+h/2+170,C.navy,C.white,1,40);}
SC.check=(t,s)=>{bgFill(C.mint,C.teal);const k=pop(t,s.start);g.save();g.translate(540,860);g.scale(k,k);g.rotate(wob(t,2,0.05));
  g.fillStyle=C.purple;g.beginPath();g.arc(0,0,230,0,7);g.fill();g.strokeStyle=C.white;g.lineWidth=46;g.lineCap='round';g.beginPath();g.moveTo(-110,10);g.lineTo(-30,90);g.lineTo(120,-80);g.stroke();eyes(0,-120,40,t);g.restore();};
SC.deeds=(t,s)=>{bgFill(C.purple,C.violet);const xs=[250,540,830];const per=(s.end-s.start)/3;
  xs.forEach((x,i)=>{const k=pop(t,s.start+i*per);g.save();g.translate(x,860);g.scale(k,k);
   if(i==0){rr(-90,-160,180,320,30,C.teal);g.fillStyle=C.violet;g.beginPath();g.moveTo(-60,-60);g.quadraticCurveTo(0,-170,60,-60);g.closePath();g.fill();}
   if(i==1){rr(-120,-70,240,170,26,C.yellow);rr(-50,-110,100,50,16,C.yellow);g.fillStyle=C.purple;g.fillRect(-120,-10,240,14);}
   if(i==2){g.fillStyle=C.magenta;g.beginPath();g.moveTo(0,90);g.bezierCurveTo(-150,-20,-70,-140,0,-60);g.bezierCurveTo(70,-140,150,-20,0,90);g.fill();coin(0,-10,34);}
   eyes(0,i==2?60:0,32,t);g.restore();});
  ['pray','work','give'].forEach((w,i)=>pill(w,xs[i],1110,C.navy,C.white,prog(t,s.start+i*per+0.2,s.start+i*per+0.5),40));};
SC.night=(t,s)=>{bgFill('#07051A','#120D35');g.fillStyle=C.cream;g.beginPath();g.arc(820,380,90,0,7);g.fill();g.fillStyle='#07051A';g.beginPath();g.arc(860,350,80,0,7);g.fill();
  confetti(t,C.white,0.2);const k=pop(t,s.start);const gl=g.createRadialGradient(540,880,0,540,880,420);gl.addColorStop(0,'rgba(110,43,224,0.55)');gl.addColorStop(1,'rgba(110,43,224,0)');g.fillStyle=gl;g.fillRect(0,400,W,1000);
  g.save();g.translate(540,880);g.scale(k,k);rr(-120,-210,240,420,36,C.navy);rr(-100,-180,200,350,22,C.violet);eyes(0,-20,46,t,-1.5);g.restore();
  pill('this habit',540,1200,C.red,C.white,prog(t,s.start+1,s.start+1.3),46);};
SC.heavy=(t,s)=>{bgFill(C.deep,C.navy);const p3=(s.end-s.start)/3;const k=pop(t,s.start);
  g.save();g.translate(330,860+Math.sin(t*2)*8);g.scale(k,k);g.fillStyle=C.magenta;g.beginPath();g.moveTo(0,90);g.bezierCurveTo(-150,-20,-70,-140,0,-60);g.bezierCurveTo(70,-140,150,-20,0,90);g.fill();eyes(0,-20,30,t);g.restore();
  const w=pop(t,s.start+0.4);g.save();g.translate(330,700-40*(1-w));g.scale(w,w);rr(-70,-50,140,100,20,'#555577');g.fillStyle=C.white;g.font='600 40px Inter';g.textAlign='center';g.fillText('kg',0,14);g.restore();
  const k2=pop(t,s.start+p3);g.save();g.translate(760,800);g.scale(k2,k2);for(let i=0;i<5;i++){g.fillStyle=`rgba(155,92,246,${0.25+0.1*i})`;g.beginPath();g.arc(Math.sin(t+i)*40,Math.cos(t*0.8+i)*30,90-i*10,0,7);g.fill();}eyes(0,0,30,t);g.restore();
  pill('focus: gone',760,1000,C.violet,C.white,prog(t,s.start+p3,s.start+p3+0.3),38);
  const k3=pop(t,s.start+2*p3);g.save();g.translate(540,1170);g.scale(k3,k3);pill('barakah: blocked',0,0,C.red,C.white,1,44);g.restore();};
SC.allah=(t,s)=>{bgFill(C.navy,'#241A6B');const k=pop(t,s.start);g.save();g.translate(540,860);g.scale(k,k);
  for(let i=0;i<12;i++){g.save();g.rotate(i*Math.PI/6+t*0.2);g.fillStyle='rgba(249,228,91,0.12)';g.beginPath();g.moveTo(0,0);g.lineTo(-60,-520);g.lineTo(60,-520);g.fill();g.restore();}
  g.fillStyle=C.cream;g.beginPath();g.moveTo(0,-110);g.quadraticCurveTo(-150,-160,-300,-110);g.lineTo(-300,140);g.quadraticCurveTo(-150,90,0,140);g.closePath();g.fill();g.beginPath();g.moveTo(0,-110);g.quadraticCurveTo(150,-160,300,-110);g.lineTo(300,140);g.quadraticCurveTo(150,90,0,140);g.closePath();g.fill();
  g.strokeStyle=C.violet;g.lineWidth=8;for(let i=0;i<4;i++){g.beginPath();g.moveTo(-250,-50+i*45);g.lineTo(-50,-50+i*45);g.moveTo(50,-50+i*45);g.lineTo(250,-50+i*45);g.stroke();}g.restore();};
SC.q1=(t,s)=>quoteCard(t,s,['Tell the believing men','to lower their gaze','and guard their chastity.','That is purer for them.'],'Quran 24:30',C.magenta,C.purple,C.magenta);
SC.protect=(t,s)=>{bgFill(C.cream);const k=pop(t,s.start);g.save();g.translate(540,860);g.scale(k,k);g.rotate(wob(t,2,0.04));
  g.fillStyle=C.teal;g.beginPath();g.moveTo(0,-240);g.lineTo(200,-160);g.quadraticCurveTo(200,120,0,240);g.quadraticCurveTo(-200,120,-200,-160);g.closePath();g.fill();
  g.fillStyle=C.mint;g.beginPath();g.moveTo(0,-180);g.lineTo(140,-120);g.quadraticCurveTo(140,90,0,180);g.closePath();g.fill();eyes(0,-20,50,t);g.restore();
  pill('not punishment',540,450,C.red,C.white,prog(t,s.start,s.start+0.3)*(1-prog(t,s.start+1.6,s.start+1.9)),42);pill('protection',540,1180,C.navy,C.white,prog(t,s.start+1.7,s.start+2),52);};
SC.start=(t,s)=>{bgFill(C.purple,C.violet);burst(540,860,300,C.violet,t);const k=pop(t,s.start);g.save();g.translate(540,860);g.scale(k,k);g.fillStyle=C.white;g.font='600 200px Inter';g.textAlign='center';g.fillText('3',0,70);g.restore();pill('steps to start',540,1150,C.yellow,C.navy,prog(t,s.start+0.3,s.start+0.6),48);};
SC.s1=(t,s)=>{bgFill(C.mint,C.teal);const k=pop(t,s.start);g.save();g.translate(380,880);g.scale(k,k);rr(-150,-280,300,560,20,C.purple);rr(-130,-260,260,520,14,C.violet);g.fillStyle=C.yellow;g.beginPath();g.arc(100,20,16,0,7);g.fill();g.restore();
  const p=ease(prog(t,s.start+0.6,s.start+1.6));g.save();g.translate(380-120+p*520,980);g.rotate(0.15);rr(-55,-95,110,190,22,C.navy);rr(-44,-80,88,150,12,C.mint);eyes(0,-10,22,t,1);g.restore();
  pill('1. Phone outside the bedroom',540,1220,C.navy,C.white,1,40);};
SC.s2=(t,s)=>{bgFill(C.navy,C.deep);const k=pop(t,s.start);g.save();g.translate(380,860);g.scale(k,k);rr(-120,-40,240,200,30,C.yellow);g.strokeStyle=C.yellow;g.lineWidth=30;g.beginPath();g.arc(0,-40,80,Math.PI,0);g.stroke();eyes(0,60,34,t);g.restore();
  const p=ease(prog(t,s.start+1.6,s.start+2.8));g.save();g.translate(560+p*220,860-Math.sin(p*Math.PI)*120);g.rotate(p*2);g.fillStyle=C.teal;g.beginPath();g.arc(0,0,40,0,7);g.fill();g.fillRect(30,-12,110,24);g.fillRect(110,12,18,30);g.restore();
  g.fillStyle=C.magenta;g.beginPath();g.arc(840,880,70,0,7);g.fill();eyes(840,880,26,t,-1);
  pill('2. Blocker + trusted friend',540,1220,C.teal,C.navy,1,40);};
SC.s3=(t,s)=>{bgFill(C.magenta,C.purple);const k=pop(t,s.start);g.save();g.translate(540,860);g.scale(k,k);
  const gl=g.createRadialGradient(0,-40,0,0,-40,330);gl.addColorStop(0,'rgba(249,228,91,0.9)');gl.addColorStop(1,'rgba(249,228,91,0)');g.fillStyle=gl;g.fillRect(-340,-380,680,680);
  rr(-130,-240,260,420,130,C.yellow);g.fillStyle=C.cream;g.beginPath();g.roundRect(-100,-210,200,390,100);g.fill();g.restore();
  const p=ease(prog(t,s.start+1.2,s.end));g.strokeStyle=C.white;g.lineWidth=14;g.setLineDash([24,20]);g.beginPath();g.moveTo(140,1350);g.quadraticCurveTo(300,1100-200*p,540,1050);g.stroke();g.setLineDash([]);
  pill('3. Run back to Him',540,1250,C.navy,C.white,1,42);};
SC.q2=(t,s)=>quoteCard(t,s,['O My servants who have','exceeded the limits against','their souls! Do not lose hope','in Allah’s mercy, for Allah','certainly forgives all sins.'],'Quran 39:53',C.teal,C.navy,C.teal);
SC.win=(t,s)=>{bgFill(C.cream);const k=pop(t,s.start);g.save();g.translate(540,860);g.scale(k,k);rr(-330,-260,660,520,40,C.white);rr(-330,-260,660,110,40,C.purple);
  for(let i=0;i<14;i++){const x=-260+(i%7)*87,y=-90+Math.floor(i/7)*130;rr(x-34,y-34,68,68,16,'#EDE7FB');const on=prog(t,s.start+0.3+i*0.18,s.start+0.45+i*0.18);if(on>0){g.save();g.translate(x,y);g.scale(on,on);g.fillStyle=C.teal;g.beginPath();g.arc(0,0,30,0,7);g.fill();g.restore();}}
  g.restore();pill('day by day',540,1200,C.navy,C.white,1,44);};
SC.cta=(t,s)=>{bgFill(C.purple,C.magenta);burst(540,860,320,C.violet,t);const p=ease(prog(t,s.start,s.end));g.save();g.translate(200+640*p,1050-420*p);g.rotate(-0.4);g.scale(1.8,1.8);
  g.fillStyle=C.white;g.beginPath();g.moveTo(-60,10);g.lineTo(70,-40);g.lineTo(-10,40);g.lineTo(-20,15);g.closePath();g.fill();g.fillStyle=C.yellow;g.beginPath();g.moveTo(-20,15);g.lineTo(70,-40);g.lineTo(-5,22);g.closePath();g.fill();g.restore();
  pill('Send this, quietly',540,1200,C.navy,C.white,1,50);};
