import Link from 'next/link'
import useSWR from 'swr'
import fetch from 'unfetch'
const fetcher = url => fetch(url).then(r => r.json())

// This function gets called at build time
// export async function getStaticPaths () {
//   // nothing static here
//   return { paths: ['/reports/plone/guillotina'], fallback: true }
// }

function Reports ({ params }) {
  const { data, error } = useSWR(
    `${process.env.NEXT_PUBLIC_API_URL}/recent-reports`,
    fetcher
  )
  if (!data) {
    return <ul />
  }
  return (
    <ul>
      {data.map((value, index) => {
        return (
          <li key={index}>
            <Link
              href={
                '/reports/' +
                params.org +
                '/' +
                params.repo +
                '/' +
                value.commit_hash
              }
            >
              <a>
                {value.branch}: {value.commit_hash}
              </a>
            </Link>
          </li>
        )
      })}
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

export default Reports
