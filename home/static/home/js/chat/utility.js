export function makeNotification(n) {
    changeIcon('/static/home/images/notification-icon.ico');
    try {
        new Audio('/static/home/sounds/notification.mp3').play();
    } catch (e) {}

    if (Notification && Notification.permission == 'granted') {
        let notification = new Notification(n.title, {
            icon: n.link,
            body: n.body,
        });
        notification.onclick = function() {
            if (window.location.pathname !== "/chat/") {
                window.location.href = "/chat#room_id=" + n.room_id;
            }
        };
    }
}

export function removeNotification() {
    changeIcon('/static/home/images/favicon.ico');
}

export function changeIcon(resource) {
    let link = document.querySelector("link[rel~='icon']");
    if (!link) {
        link = document.createElement('link');
        link.rel = 'icon';
        document.getElementsByTagName('head')[0].appendChild(link);
    }
    link.href = resource;
}

export function formatDate(someDateTimeStamp) {
    let fulldays = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
    let months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    let dt = new Date(someDateTimeStamp),
        date = dt.getDate(),
        month = _(months[dt.getMonth()]),
        timeDiff = someDateTimeStamp - Date.now(),
        diffDays = new Date().getDate() - date,
        diffMonths = new Date().getMonth() - dt.getMonth(),
        diffYears = new Date().getFullYear() - dt.getFullYear();

    if (diffYears === 0 && diffDays === 0 && diffMonths === 0) {
        return _("Today");
    } else if (diffYears === 0 && diffMonths === 0 && diffDays === 1) {
        return _("Yesterday");
    } else if (diffYears === 0 && diffMonths === 0 && diffDays === -1) {
        return _("Tomorrow");
    } else if (diffYears === 0 && diffMonths === 0 && (diffDays > 1 && diffDays < 7)) {
        return _(fulldays[dt.getDay()]);
    } else if (diffYears >= 1) {
        return month + " " + date + ", " + new Date(someDateTimeStamp).getFullYear();
    } else {
        return month + " " + date;
    }
}

export function formatTime(ts) {
    let date = new Date(ts);
    let hours = date.getHours();
    let minutes = "0" + date.getMinutes();
    let seconds = "0" + date.getSeconds();
    return hours + ':' + minutes.substr(-2) + ':' + seconds.substr(-2);
}

export function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

export class Lock {
    constructor() {
        this.__locked = false;
        this.promises = [];
    }

    lock() {
        if (this.__locked) {
            throw new Error("[LockError] Locking locked lock");
        }
        this.__locked = true;
    }

    unlock() {
        if (!this.__locked) {
            throw new Error("[LockError] Unlocking unlocked lock");
        }
        this.__locked = false;
        for (let resolver of this.promises) {
            resolver();
        }
        this.promises = [];
    }

    locked() {
        return this.__locked;
    }

    wait() {
        let ctx = this;
        return new Promise((resolve, reject) => {
            ctx.promises.push(resolve);
        })
    }
}

export async function getImageSize(src) {
    // if (src instanceof Blob) {
    //   let reader = new FileReader();
    //    reader.onload = function(){
    //      let dataURL = reader.result;
    //    };
    //  reader.readAsDataURL(input.files[0]);
    // }
    const img = new Image();
    return new Promise((resolve, reject) => {
        img.onload = function() {
            resolve({ w: this.width, h: this.height });
        }
        img.src = src;
    })
}

export function parseParms(str) {
    let pieces = str.split("&"),
        data = {},
        i, parts;
    // process each query pair
    for (i = 0; i < pieces.length; i++) {
        parts = pieces[i].split("=");
        if (parts.length < 2) {
            parts.push("");
        }
        data[decodeURIComponent(parts[0])] = decodeURIComponent(parts[1]);
    }
    return data;
}

export function _(s) {
    let translation = TRANSLATIONS[s];
    if (translation !== undefined) {
        return translation;
    }
    console.warn("translation for '" + s + "' was not passed to JS. Take a look at chat.views.get_translations");
    return s;
}

export function setCaretPosition(elem, caretPos) {

    if (elem == null) {
        return
    }

    if (elem.createTextRange) {
        var range = elem.createTextRange();
        range.move('character', caretPos);
        range.select();
    } else {
        if (elem.selectionStart) {
            elem.focus();
            elem.setSelectionRange(caretPos, caretPos);
        } else {
            elem.focus();
        }
    }
}