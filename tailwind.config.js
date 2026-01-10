/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './chat/templates/**/*.html', // path to your Django templates
    './node_modules/flowbite/**/*.js' // include Flowbite JS
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('flowbite/plugin') // enable Flowbite plugin
  ],
}