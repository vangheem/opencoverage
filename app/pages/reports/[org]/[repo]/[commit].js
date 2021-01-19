import useSWR from 'swr'
import fetch from 'unfetch'
const fetcher = url => fetch(url).then(r => r.json())

function Report ({ params }) {
  const { data, error } = useSWR(
    `http://localhost:8000/reports/${params.org}/${params.repo}/${params.commit}`,
    fetcher
  )
  if (!data) {
    return <div />
  }
  return (
    <ul>
      <li>hi</li>
    </ul>
  )
}

// This also gets called at build time
export async function getServerSideProps ({ params }) {
  // params contains the post `id`.
  // If the route is like /posts/1, then params.id is 1
  //   const res = await fetch(`https://.../posts/${params.id}`)
  //   const post = await res.json()

  // Pass post data to the page via props
  return {
    props: {
      params
    }
  }
}

export default Report
