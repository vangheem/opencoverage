import Menu from './menu.js'
import Head from 'next/head'

export default function Header ({ title }) {
  if (!title) {
    title = 'Open Coverage: Free and open source coverage reporting'
  }
  return (
    <>
      <Head>
        <title>{title}</title>
        <link rel='icon' href='/logo/logo2-o.png' />
        <link rel='shortcut icon' href='/logo/logo2-o.png' />
        <link rel='apple-touch-icon' href='/logo/logo2-o.png' />
      </Head>
      <Menu />
    </>
  )
}
