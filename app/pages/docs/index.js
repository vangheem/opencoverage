import Layout from '../../components/layout'

export async function getStaticPaths () {
  // nothing static here
  return { paths: ['/docs'], fallback: true }
}

export async function getStaticProps (context) {
  return {
    props: {} // will be passed to the page component as props
  }
}

function Docs ({ params }) {
  return (
    <Layout title='Documentation: Open Coverage'>
      <div className='container'>
        <br />
        <h1 className='title'>Open Coverage Documentation</h1>

        <div className='section'>
          <a href='/docs/integration' className='box'>
            <h2 className='title'>Integration</h2>
            Integrating with your open source project
          </a>
          <a href='/docs/hosting' className='box'>
            <h2 className='title'>Hosting</h2>
            Host private projects yourself
          </a>
          <a href='https://github.com/vangheem/opencoverage' className='box'>
            <h2 className='title'>Contribute</h2>
            Contribute to improving Open Coverage
          </a>
        </div>
      </div>
    </Layout>
  )
}

export default Docs
