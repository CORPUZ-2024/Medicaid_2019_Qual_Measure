/* Small Markdown -> HTML for the prose pages. Handles: ATX headings (with an
   optional leading <a id="..."></a> anchor), fenced code blocks, bold/italic,
   links, inline code, unordered lists with wrapped continuation lines,
   GitHub-style tables, and paragraphs. Not full CommonMark - just what the .md
   files in this repo use. */
function mdToHtml(src){
  const esc = s => s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  const inline = s => esc(s)
    .replace(/`([^`]+)`/g,'<code>$1</code>')
    .replace(/\*\*([^*]+)\*\*/g,'<b>$1</b>')
    .replace(/(^|[^*])\*([^*\n]+)\*/g,'$1<i>$2</i>')
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g,'<a href="$2">$1</a>');

  const lines = src.replace(/\r\n/g,'\n').split('\n');
  const out=[]; let i=0;

  while(i<lines.length){
    let l=lines[i];

    if(/^\s*$/.test(l)){ i++; continue; }

    // fenced code block
    if(/^\s*```/.test(l)){
      i++; const buf=[];
      while(i<lines.length && !/^\s*```/.test(lines[i])){ buf.push(lines[i]); i++; }
      i++; // closing fence
      out.push(`<pre class="mono" style="background:#f2f4f7;padding:12px 14px;border-radius:8px;overflow-x:auto;font-size:12.5px">${esc(buf.join('\n'))}</pre>`);
      continue;
    }

    // heading, optionally prefixed with an <a id="..."></a> anchor
    let m = l.match(/^(#{1,4})\s+(?:<a\s+id="([^"]+)"><\/a>\s*)?(.*)$/);
    if(m){
      const lvl=m[1].length, id=m[2]?` id="${m[2]}"`:'', txt=inline(m[3]);
      out.push(`<h${lvl}${id}>${txt}</h${lvl}>`); i++; continue;
    }

    // table
    if(l.trim().startsWith('|')){
      const tbl=[]; while(i<lines.length && lines[i].trim().startsWith('|')){ tbl.push(lines[i]); i++; }
      const cells = r => r.trim().replace(/^\||\|$/g,'').split('|').map(c=>c.trim());
      const head=cells(tbl[0]); const body=tbl.slice(2).map(cells);
      out.push('<div class="scroll"><table><thead><tr>'+
        head.map(h=>`<th>${inline(h)}</th>`).join('')+'</tr></thead><tbody>'+
        body.map(r=>'<tr>'+r.map(c=>`<td>${inline(c)}</td>`).join('')+'</tr>').join('')+
        '</tbody></table></div>');
      continue;
    }

    // unordered list, with wrapped continuation lines
    if(/^\s*[-*]\s+/.test(l)){
      const items=[];
      while(i<lines.length && /^\s*[-*]\s+/.test(lines[i])){
        let text=lines[i].replace(/^\s*[-*]\s+/,''); i++;
        while(i<lines.length && !/^\s*$/.test(lines[i]) &&
              !/^\s*[-*]\s+/.test(lines[i]) && !/^\s*```/.test(lines[i]) &&
              !lines[i].trim().startsWith('|') && !/^#{1,4}\s/.test(lines[i])){
          text += ' ' + lines[i].trim(); i++;
        }
        items.push(text);
      }
      out.push('<ul>'+items.map(t=>`<li>${inline(t)}</li>`).join('')+'</ul>');
      continue;
    }

    // paragraph
    const para=[];
    while(i<lines.length && !/^\s*$/.test(lines[i]) && !/^#{1,4}\s/.test(lines[i]) &&
          !lines[i].trim().startsWith('|') && !/^\s*[-*]\s+/.test(lines[i]) &&
          !/^\s*```/.test(lines[i])){
      para.push(lines[i]); i++;
    }
    out.push(`<p>${inline(para.join(' '))}</p>`);
  }
  return out.join('\n');
}
