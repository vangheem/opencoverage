import Header from '../components/header'
import Footer from '../components/footer'
import Report from '../components/report'
import useSWR from 'swr'
import { fetcher, apiUrl } from '../utils'

export function RecentPRs () {
  const { data, error } = useSWR(`${apiUrl}/recent-pr-reports`, fetcher)
  if (!data) {
    return <div />
  }
  if (data.result.length == 0) {
    return <div>No recent PRs</div>
  }
  return (
    <div>
      <h3>Recent Pull Requests</h3>
      {data.result.map((report, index) => {
        return <Report report={report} key={index} />
      })}
    </div>
  )
}

export function RecentCommits () {
  const { data, error } = useSWR(
    `${apiUrl}/recent-reports?branch=master`,
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

export default function Home () {
  return (
    <div className='container'>
      <Header />

      <RecentPRs />
      <RecentCommits />

      <Footer />
    </div>
  )
}
