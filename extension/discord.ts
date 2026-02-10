const scrapeConvoDiscord = () => {
    const bList = ["Bradley Boratto", "b4", "b4444"]
    const fmtName = (n: string) => bList.includes(n) ? 'b4444' : n.toLowerCase().replace(/[^a-z0-9]+/g, "-")

    const msgs = [...document.querySelectorAll('[id^="chat-messages"]')].map(m => {
        const nameEl = m.querySelector('[id^="message-username"] [role=button]') as HTMLDivElement | null
        const contentEl = m.querySelector('[id^="message-content"]') as HTMLDivElement | null
        if (!nameEl?.innerText || !contentEl) return null
        const name = fmtName(nameEl.innerText)
        return { name, role: name == "b4444" ? "assistant" : "user", content: contentEl.innerText }
    }).filter(x => x != null).slice(-7)
    
    console.log(msgs)

    const partial = (document.querySelector('[role=textbox]') as HTMLDivElement | null)
        ?.textContent?.split('\u200b')?.[0]?.trim()

    const text = '<|im_start|>system\ncontinue this discord conversation (you are b4444) (there may be a partial message already, if so, continue typing from that point onwards, completing the message, withourt retyping the first part) (never include "b4444:" or attempt to respond as any other user, just continue the conversation) /nothink <|im_end|>\n' +
        msgs.map(m => `<|im_start|>${m.role}\n${m.name}: ${m.content}<|im_end|>`).join('\n') +
        (partial ? `\n<|im_start|>assistant\nb4444: ${partial}` : '')

    return text
}


const ollamaFetch = async (text: string, model = 'discordqwen14b') => {
    const doFrequentUpdates = true

    const prompt = scrapeConvoDiscord()
    const response = await fetch('http://localhost:11434/api/generate',
        { method: 'POST', body: JSON.stringify({ model, prompt }) })

    const reader = response.body!.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
        const { done, value } = await reader.read()
        if (done) return buffer.trim()
        const chunk = JSON.parse(decoder.decode(value))
        buffer += chunk.response
        if(doFrequentUpdates) suggestDiscord(buffer)
    }
}

document.onreadystatechange = () => {
    addEventListener('keydown', (ev) => {
        if (ev.key == 'Tab' && ev.shiftKey) {
            acceptSuggestion()
            ev.preventDefault()
        } else if (ev.key == 'Tab') {
            ollamaFetch(scrapeConvoDiscord())
            ev.preventDefault()
        }
    })
}

// place the suggested text after • (we do this by highlighting starting with/including • and insserting)
const suggestDiscord = (text: string) => {
    const el = document.querySelector('[role="textbox"]') as HTMLDivElement | null
    if (!el) return
    el.style.outline = 'none'
    el.focus()

    selectFromMarker(el)
    el.dispatchEvent(new InputEvent('beforeinput', {
        data: '\u200b' + text.replaceAll('\n', ' '), inputType: 'insertText', bubbles: true, cancelable: true
    }))
    setTimeout(() => moveBeforeMarker(el), 0)
}

const selectFromMarker = (el: HTMLElement) => {
    const sel = window.getSelection()!
    sel.removeAllRanges()
    const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT)
    let node: Text | null
    while (node = walker.nextNode() as Text | null) {
        const idx = node.textContent?.indexOf('\u200b') ?? -1
        if (idx === -1) continue
        const range = document.createRange()
        range.setStart(node, idx)
        range.setEnd(node, node.textContent!.length)
        sel.addRange(range)
        return
    }
    // no bullet — collapse to end
    sel.selectAllChildren(el)
    sel.collapseToEnd()
}

const moveBeforeMarker = (el: HTMLElement) => {
    const sel = window.getSelection()!
    sel.removeAllRanges()
    const range = document.createRange()
    const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT)
    let node: Text | null
    while (node = walker.nextNode() as Text | null) {
        const idx = node.textContent?.indexOf('\u200b') ?? -1
        if (idx === -1) continue
        range.setStart(node, idx)
        range.collapse(true)
        sel.addRange(range)
        return
    }
}

const acceptSuggestion = () => {
    const el = document.querySelector('[role="textbox"]') as HTMLDivElement | null
    if (!el) return
    el.focus()
    // select just the marker character and replace with nothing
    const sel = window.getSelection()!
    sel.removeAllRanges()
    const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT)
    let node: Text | null
    while (node = walker.nextNode() as Text | null) {
        const idx = node.textContent?.indexOf('\u200b') ?? -1
        if (idx === -1) continue
        const range = document.createRange()
        range.setStart(node, idx)
        range.setEnd(node, idx + 1)
        sel.addRange(range)
        el.dispatchEvent(new InputEvent('beforeinput', {
            data: '', inputType: 'insertText', bubbles: true, cancelable: true
        }))
        setTimeout(() => {
            sel.selectAllChildren(el)
            sel.collapseToEnd()
        }, 0)
        return
    }
}

suggestDiscord('test dispatch')


console.log({ ollamaFetch, scrapeConvoDiscord, dispatchDiscord: suggestDiscord })