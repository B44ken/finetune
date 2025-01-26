// fill out the names map, at least with your own name
const names = {
    "Display Name": "user_name",
}

const format = (el) => {
    const contents = el.children[0]?.querySelector('[class^=contents]')
    let message = ''
    try {
        let username = contents.querySelector('[class^=username]').innerText
        username = names[username] || username
        const time = contents.querySelector('[class^=timestamp]').innerText
        const timeFormat = /\d+:\d+/.exec(time)[0] + ':00'
        message += `${username}, ${timeFormat}: `
    } catch(err) { }
    const text = contents.querySelector('[id^=message-content]').innerText
    message += text
    return message
}

document.querySelectorAll('li[id^="chat-messages"]').slice(-10).map(e => format(e)).join('\n')