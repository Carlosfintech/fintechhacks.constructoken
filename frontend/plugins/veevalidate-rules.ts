import { defineRule, configure } from "vee-validate"
import { required, email, min, max, url } from "@vee-validate/rules"
import { localize } from "@vee-validate/i18n"
import { apiActivity } from "@/api"

export default defineNuxtPlugin((nuxtApp) => {
  defineRule("required", required)
  defineRule("email", email)
  defineRule("min", min)
  defineRule("max", max)
  defineRule("url", url)
  // @ts-ignore
  defineRule("identity", async (value, [target], ctx) => {
    // https://vee-validate.logaretm.com/v4/guide/global-validators#cross-field-validation
    if (ctx.form[target]) {
      try {
        const { status } = await apiActivity.checkPersonaName(value as string)
        if (status.value == "success") return true
        else return false
      } catch (error) {
        return false
      }
    } else return true
  })
  // @ts-ignore
  defineRule("confirmed", (value, [target], ctx) => {
    // https://vee-validate.logaretm.com/v4/guide/global-validators#cross-field-validation
    if (value === ctx.form[target]) {
      return true
    }
    return false
  })
})

configure({
  // Generates an English message locale generator
  generateMessage: localize({
    en: {
      messages: {
        required: "This field is required.",
        email: "This email address is invalid.",
        min: "Passwords must be 8 to 64 characters long.",
        max: "Passwords must be 8 to 64 characters long.",
        url: "This url is invalid.",
        confirmed: "Passwords must match.",
        identity: "This identity name is invalid.",
      },
    },
    fr: {
      messages: {
        required: "Ce champ est obligatoire.",
        email: "Cette adresse e-mail n'est pas valide.",
        min: "Les mots de passe doivent comporter entre 8 et 64 caractères.",
        max: "Les mots de passe doivent comporter entre 8 et 64 caractères.",
        url: "Cette URL n'est pas valide.",
        confirmed: "Les mots de passe doivent correspondre.",
        identity: "Ce nom d'identité n'est pas valide.",
      },
    },
  }),
})

/*
  References:

  https://vee-validate.logaretm.com/v4/guide/overview/
  https://github.com/razorcx-courses/nuxt3-veevalidate
  https://vee-validate.logaretm.com/v4/guide/global-validators/#available-rules
  https://vee-validate.logaretm.com/v4/guide/i18n
  https://stackblitz.com/edit/vee-validate-v4-async-validation-ghqzvibx?file=src%2FApp.vue
*/
