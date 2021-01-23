import Header from '../../../../components/header'
import Footer from '../../../../components/footer'
import Report from '../../../../components/report'
import useSWR from 'swr'
import { fetcher, apiUrl } from '../../../../utils'

export function RecentCommits ({ params }) {
  const { data, error } = useSWR(
    `${apiUrl}/${params.org}/repos/${params.repo}/reports`,
    fetcher
  )
  if (!data) {
    return <div />
  }
  if (data.result.length == 0) {
    return <div>No recent commits</div>
  }
  return (
    <div>
      <h3>Recent Commits</h3>
      {data.result.map((report, index) => {
        return <Report report={report} key={index} />
      })}
    </div>
  )
}

export default function RepoHome ({ params }) {
  return (
    <div className='container'>
      <Header />

      <RecentCommits params={params} />

      <Footer />
    </div>
  )
}

// This also gets called at build time
export async function getServerSideProps ({ params }) {
  // Pass post data to the page via props
  return {
    props: {
      params
    }
  }
}
