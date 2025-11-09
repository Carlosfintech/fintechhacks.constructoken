function readableDate(term: Date | string, showYear: boolean = true) {
  // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date/toLocaleDateString
  // https://stackoverflow.com/a/66590756/295606
  // https://stackoverflow.com/a/67196206/295606
  const readable = term instanceof Date ? term : new Date(term)
  const day = readable.toLocaleDateString("en-UK", { day: "numeric" })
  const month = readable.toLocaleDateString("en-UK", { month: "short" })
  if (showYear) {
    const year = readable.toLocaleDateString("en-UK", { year: "numeric" })
    return `${day} ${month} ${year}`
  }
  return `${day} ${month}`
}

function readableNumber(term: string | number, trunc: boolean = false): string {
  // https://stackoverflow.com/a/2901298/295606
  // https://stackoverflow.com/a/10601315/295606
  if (!term) return "n/a"
  if (typeof term === "string") term = parseInt(term)
  if (trunc && term >= 1000) {
    const suffixes: string[] = ["k", "m", "b", "t"]
    for (let suffixNum = suffixes.length - 1; suffixNum >= 0; suffixNum--) {
      const scale = Math.pow(10, (suffixNum + 1) * 3)
      if (scale <= term) {
        term = Math.floor((term * 10) / scale) / 10
        if (term === 1000 && suffixNum < suffixes.length - 1) {
          term = 1
          suffixNum++
        }
        return suffixes[suffixNum] !== null
          ? // @ts-ignore
            term + suffixes[suffixNum]
          : `${term}`
      }
    }
    // const suffixNum = Math.floor(("" + term).length / 3)
    // let shortValue
    // for (let precision = 2; precision >= 1; precision--) {
    //   shortValue = parseFloat(
    //     (suffixNum !== 0 ? term / Math.pow(1000, suffixNum) : term).toPrecision(
    //       precision
    //     )
    //   )
    //   const dotLessShortValue = (shortValue + "").replace(/[^a-zA-Z 0-9]+/g, "")
    //   if (dotLessShortValue.length <= 2) {
    //     break
    //   }
    // }
    // if (shortValue % 1 !== 0) shortValue = shortValue.toFixed(1)
    // return shortValue + suffixes[suffixNum]
  }
  return term.toString().replace(/\B(?<!\.\d*)(?=(\d{3})+(?!\d))/g, ",")
}

export { readableDate, readableNumber }
