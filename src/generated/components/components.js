(()=>{
  document.documentElement.dataset.interactiveReady='true';
  document.addEventListener('click',event=>{
    const target=event.target.closest('button');if(!target)return;const specimen=target.closest('.specimen');if(!specimen)return;
    if(target.dataset.feedback){specimen.querySelector('.feedback').textContent=target.dataset.feedback}
    if(target.hasAttribute('data-icon-toggle')){const pressed=target.getAttribute('aria-pressed')!=='true';target.setAttribute('aria-pressed',String(pressed));specimen.querySelector('.feedback').textContent=pressed?'설정을 선택했습니다.':'설정 선택을 해제했습니다.'}
    if(target.classList.contains('switch')){const checked=target.getAttribute('aria-checked')!=='true';target.setAttribute('aria-checked',String(checked));const label=specimen.querySelector('[data-switch-label]');if(label)label.textContent=checked?'알림 사용 중':'알림 사용 안 함'}
    if(target.dataset.tab){specimen.querySelectorAll('[data-tab]').forEach(tab=>{const on=tab===target;tab.classList.toggle('on',on);tab.setAttribute('aria-selected',String(on))});specimen.querySelectorAll('[data-panel]').forEach(panel=>panel.hidden=panel.dataset.panel!==target.dataset.tab)}
    if(target.hasAttribute('data-dialog-open'))specimen.querySelector('dialog').showModal();if(target.hasAttribute('data-dialog-close'))target.closest('dialog').close();
    if(target.hasAttribute('data-panel-toggle')){const panel=specimen.querySelector('.interactive-panel');panel.hidden=!panel.hidden;target.textContent=panel.hidden?(specimen.dataset.componentCase==='Sheet'?'필터 상세 열기':'추가 옵션 열기'):'패널 닫기'}
    if(target.dataset.page){const pages=[...specimen.querySelectorAll('[data-page="1"],[data-page="2"]')];let index=pages.findIndex(page=>page.hasAttribute('aria-current'));if(target.dataset.page==='prev')index=Math.max(0,index-1);else if(target.dataset.page==='next')index=Math.min(pages.length-1,index+1);else index=pages.indexOf(target);pages.forEach((page,i)=>{page.classList.toggle('on',i===index);if(i===index)page.setAttribute('aria-current','page');else page.removeAttribute('aria-current')})}
    if(target.hasAttribute('data-dismiss')){specimen.querySelector('.alert').hidden=true;specimen.querySelector('.feedback').textContent='알림을 확인했습니다.'}
    if(target.hasAttribute('data-progress')){const bar=specimen.querySelector('[role="progressbar"]'),next=Number(bar.getAttribute('aria-valuenow'))>=100?0:Math.min(100,Number(bar.getAttribute('aria-valuenow'))+19);bar.setAttribute('aria-valuenow',String(next));bar.querySelector('span').style.width=`${next}%`;specimen.querySelector('[data-progress-label]').textContent=`처리 진행률 ${next}%`}
    if(target.hasAttribute('data-toast-open'))specimen.querySelector('.toast').hidden=false;if(target.hasAttribute('data-toast-close'))target.closest('.toast').hidden=true;
    if(target.hasAttribute('data-dropzone-browse'))specimen.querySelector('[data-dropzone-input]').click();
    if(target.hasAttribute('data-dropzone-remove')){const dz=specimen.querySelector('[data-dropzone]');dz.dataset.state='idle';dz.querySelector('.dropzone-file').hidden=true;dz.querySelector('[data-dropzone-input]').value='';specimen.querySelector('.feedback').textContent='파일을 제거했습니다.'}
    if(target.hasAttribute('data-float-toggle')){const panel=specimen.querySelector('.float-panel');panel.hidden=!panel.hidden}
    if(target.hasAttribute('data-chat-send')){const input=specimen.querySelector('[data-chat-input]'),value=input.value.trim();if(value){const li=document.createElement('li');li.className='chat-msg out';li.textContent=value;const list=specimen.querySelector('.chat-msgs');list.appendChild(li);input.value='';list.scrollTop=list.scrollHeight}}
  });
  document.addEventListener('click',event=>{const cell=event.target.closest('[data-cell]');if(cell)cell.classList.toggle('selected')});
  document.querySelectorAll('[data-dropzone]').forEach(dz=>{
    const specimen=dz.closest('.specimen');
    const showFile=name=>{dz.dataset.state='filled';dz.querySelector('.dropzone-file').hidden=false;dz.querySelector('[data-dropzone-filename]').textContent=name;const feedback=specimen.querySelector('.feedback');if(feedback)feedback.textContent=`${name} 파일을 선택했습니다.`};
    dz.querySelector('[data-dropzone-input]').addEventListener('change',event=>{const file=event.target.files[0];if(file)showFile(file.name)});
    dz.addEventListener('dragover',event=>{event.preventDefault();dz.dataset.state='dragover'});
    dz.addEventListener('dragleave',()=>{if(dz.dataset.state==='dragover')dz.dataset.state='idle'});
    dz.addEventListener('drop',event=>{event.preventDefault();const file=event.dataTransfer.files[0];if(file)showFile(file.name);else dz.dataset.state='idle'});
  });
  document.querySelector('[data-input-demo]').addEventListener('input',event=>event.target.nextElementSibling.textContent=`${event.target.value.length}자 입력됨`);
  document.querySelector('[data-select-demo]').addEventListener('change',event=>event.target.nextElementSibling.textContent=`${event.target.value}을 선택했습니다.`);
})();
