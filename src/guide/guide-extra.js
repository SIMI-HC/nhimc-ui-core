(function(){
  "use strict";
  // Sandboxed viewers (Claude, ChatGPT) can block the clipboard API: select the text so Ctrl+C works.
  window.nhimcSelectText=element=>{
    const range=document.createRange();
    range.selectNodeContents(element);
    const selection=window.getSelection();
    selection.removeAllRanges();
    selection.addRange(range);
  };
  const gallery=document.getElementById("galleryView");
  const install=document.getElementById("installView");
  const sectionNav=document.getElementById("sectionNav");
  const links=[...document.querySelectorAll("#viewNav a")];
  const titles={gallery:"NHIMC UI Core · Design Guide",install:"NHIMC UI Core · 설치 가이드"};
  let first=true;
  function route(){
    const view=location.hash==="#install"?"install":"gallery";
    gallery.hidden=view!=="gallery";
    install.hidden=view!=="install";
    if(sectionNav)sectionNav.style.display=view==="gallery"?"":"none";
    links.forEach(link=>{if(link.dataset.view===view)link.setAttribute("aria-current","page");else link.removeAttribute("aria-current")});
    document.title=titles[view];
    if(view==="install"&&!first)window.scrollTo(0,0);
    first=false;
  }
  // The prompt builder always opens scrolled to the top.
  const builderDialog=document.getElementById("promptBuilderDialog");
  const resetBuilderScroll=()=>{
    builderDialog.scrollTop=0;
    const body=builderDialog.querySelector(".builder-body");
    if(body)body.scrollTop=0;
  };
  new MutationObserver(()=>{
    if(!builderDialog.open)return;
    resetBuilderScroll();
    requestAnimationFrame(resetBuilderScroll);
    setTimeout(resetBuilderScroll,80);
  }).observe(builderDialog,{attributes:true,attributeFilter:["open"]});
  window.addEventListener("hashchange",route);
  route();

  document.addEventListener("click",event=>{
    const block=event.target.closest(".copy-block pre, #builderPrompt");
    if(block&&window.getSelection().toString()==="")window.nhimcSelectText(block);
  });
  document.addEventListener("click",async event=>{
    const opener=event.target.closest("[data-open-builder]");
    if(opener){document.getElementById("builderOpen").click();return}
    const button=event.target.closest("[data-copy-target]");
    if(!button)return;
    const text=document.getElementById(button.dataset.copyTarget).textContent;
    const previous=button.textContent;
    try{await navigator.clipboard.writeText(text);button.textContent="복사됨"}
    catch(error){
      const area=document.createElement("textarea");area.value=text;area.style.position="fixed";area.style.opacity="0";
      document.body.appendChild(area);area.select();
      let done=false;
      try{done=document.execCommand("copy")}catch(fail){done=false}
      area.remove();
      if(done)button.textContent="복사됨";
      else{window.nhimcSelectText(document.getElementById(button.dataset.copyTarget));button.textContent="선택됨 · Ctrl+C"}
    }
    setTimeout(()=>{button.textContent=previous},1600);
  });
})();
