import fetch from 'unfetch'
export const apiUrl = process.env.NEXT_PUBLIC_API_URL

export function fetcher (...urls) {
  const f = u => fetch(u).then(r => r.json())

  if (urls.length > 1) {
    return Promise.all(urls.map(f))
  }
  return f(urls)
}

export function rawFetcher (...urls) {
  const f = u =>
    fetch(u).then(r => {
      return r.text()
    })

  if (urls.length > 1) {
    return Promise.all(urls.map(f))
  }
  return f(urls)
}

export function fmtRelativeDate (v) {
  if (v.indexOf('Z') === -1) {
    // convert naive to utc
    v += 'Z'
  }

  // Make a fuzzy time
  var delta = Math.round((+new Date() - Date.parse(v)) / 1000)

  var minute = 60,
    hour = minute * 60,
    day = hour * 24,
    week = day * 7

  var fuzzy

  if (delta < 30) {
    fuzzy = 'now'
  } else if (delta < minute) {
    fuzzy = delta + ' seconds ago.'
  } else if (delta < 2 * minute) {
    fuzzy = 'a minute ago.'
  } else if (delta < hour) {
    fuzzy = Math.floor(delta / minute) + ' minutes ago.'
  } else if (Math.floor(delta / hour) == 1) {
    fuzzy = '1 hour ago.'
  } else if (delta < day) {
    fuzzy = Math.floor(delta / hour) + ' hours ago.'
  } else if (delta < day * 2) {
    fuzzy = 'yesterday'
  }
  return fuzzy
}

export function fmtNumber (x) {
  return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

export function calcTagClassName (v) {
  if (v >= 0.95) {
    return 'is-link'
  } else if (v >= 0.85) {
    return 'is-info'
  } else if (v >= 0.65) {
    return 'is-warning'
  } else {
    return 'is-danger'
  }
}
