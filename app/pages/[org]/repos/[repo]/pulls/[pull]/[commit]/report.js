import useSWR from 'swr'
import Link from 'next/link'
import Layout from '../../../../../../../components/layout'
import Report from '../../../../../../../components/report'
import { fetcher, apiUrl, calcTagClassName } from '../../../../../../../utils'

function ReportUrls ({ params }) {
  const { data, error } = useSWR(
    `${apiUrl}/${params.org}/repos/${params.repo}/commits/${params.commit}/files`,
    fetcher
  )
  if (!data) {
    return <div />
  }
  return (
    <table className='table'>
      <thead>
        <tr>
          <th>Filename</th>
          <th>Coverage</th>
        </tr>
      </thead>
      <tbody>
        {data.result.map((value, index) => {
          return (
            <tr key={value.filename}>
              <td>
                <Link
                  href={
                    '/' +
                    params.org +
                    '/repos/' +
                    params.repo +
                    '/pulls/' +
                    params.pull +
                    '/' +
                    params.commit +
                    '/file?filename=' +
                    value.filename
                  }
                >
                  <a>{value.filename}</a>
                </Link>
              </td>
              <td className={calcTagClassName(value.line_rate)}>
                {(value.line_rate * 100).toFixed(1)}%
              </td>
            </tr>
          )
        })}
      </tbody>
    </table>
  )
}

function DiffReportUrls ({ report }) {
  return (
    <table className='table'>
      <thead>
        <tr>
          <th>Filename</th>
          <th>Coverage</th>
        </tr>
      </thead>
      <tbody>
        {report.pull_diff.map((value, index) => {
          return (
            <tr key={value.filename}>
              <td>
                <Link
                  href={
                    '/' +
                    report.organization +
                    '/repos/' +
                    report.repo +
                    '/pulls/' +
                    report.pull +
                    '/' +
                    report.commit_hash +
                    '/file?filename=' +
                    value.filename
                  }
                >
                  <a>{value.filename}</a>
                </Link>
              </td>
              <td className={calcTagClassName(value.line_rate)}>
                {(value.line_rate * 100).toFixed(1)}%
              </td>
            </tr>
          )
        })}
      </tbody>
    </table>
  )
}

function ReportPage ({ params }) {
  const { data, error } = useSWR(
    `${apiUrl}/${params.org}/repos/${params.repo}/pulls/${params.pull}/${params.commit}/report`,
    fetcher
  )
  if (!data) {
    return <div />
  }
  return (
    <Layout title='Report: Open Coverage'>
      <div className='container'>
        <div className='section'>
          <Report report={data} />
          <h3 className='title'>Diff coverage</h3>
          <DiffReportUrls report={data} />
          <h3 className='title'>Package coverage</h3>
          <ReportUrls params={params} />
        </div>
      </div>
    </Layout>
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

export default ReportPage
