import Layout from '../../../components/layout'

export async function getStaticPaths () {
  // nothing static here
  return { paths: ['/docs/hosting'], fallback: true }
}

export async function getStaticProps (context) {
  return {
    props: {} // will be passed to the page component as props
  }
}

function Docs ({ params }) {
  return (
    <Layout title='Contributing Documentation: Open Coverage'>
      <div className='container'>
        <br />
        <h1 className='title'>Open Coverage Documentation</h1>
        <p className='subtitle'>Contributing</p>

        <div className='section'>Some docs</div>
      </div>
      <Footer />
    </Layout>
  )
}

export default Docs
