import Menu from './menu.js'
import Head from 'next/head'

export default function Header ({ title, description }) {
  if (!title) {
    title = 'Open Coverage'
  }
  if (!description) {
    description =
      'Free and open source code coverage reporting for public and private projects. Install on-prem or use the public service.'
  }
  return (
    <>
      <Head>
        <title>{title}</title>
        <meta name='description' content={description} />

        <meta property='og:title' content={title} />
        <meta property='og:description' content={description} />
        <meta property='og:image' content='/logo/logo2-o.png' />

        <link rel='icon' href='/logo/logo2-o.png' />
        <link rel='shortcut icon' href='/logo/logo2-o.png' />
        <link rel='apple-touch-icon' href='/logo/logo2-o.png' />
      </Head>
      <Menu />
    </>
  )
}
