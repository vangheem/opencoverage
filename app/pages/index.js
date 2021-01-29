import Layout from '../components/layout'
import Report from '../components/report'
import useSWR from 'swr'
import { fetcher, apiUrl } from '../utils'

export function RecentPRs () {
  const { data, error } = useSWR(`${apiUrl}/recent-pr-reports`, fetcher)
  if (!data) {
    return <div />
  }
  if (data.result.length == 0) {
    return <div></div>
  }
  return (
    <div>
      <h3 className='title'>Recent Pull Requests</h3>
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
    return <div></div>
  }
  return (
    <div>
      <h3 className='title'>Recent Commits</h3>
      {data.result.map((report, index) => {
        return <Report report={report} key={index} />
      })}
    </div>
  )
}

export default function Home () {
  return (
    <Layout>
      <section className='hero is-dark'>
        <div className='hero-body'>
          <div className='container'>
            <img src='logo/logo2-crp.png' title='Open coverage logo' />
            <h1 className='subtitle'>
              Open coverage: Open source coverage reporting
            </h1>
          </div>
        </div>
      </section>

      <br />
      <div className='container'>
        <div className='message is-info'>
          <div className='message-body'>
            An open source project with MIT license to provide robust coverage
            reporting in your open source and private projects.
          </div>
        </div>
        <section className='section'>
          <h2 className='title'>
            Get insights directly in your pull requests.
          </h2>
          <div className='tile is-ancestor'>
            <div className='tile is-6 is-vertical is-parent'>
              <div className='tile is-child box'>
                <p className='subtitle'>Pull request comments</p>
                <img src='screenshots/comment.png' />
              </div>
            </div>
            <div className='tile is-6 is-vertical is-parent'>
              <div className='tile is-child box'>
                <p className='subtitle'>Merge checks</p>
                <img src='screenshots/check.png' />
              </div>
            </div>
          </div>
          <div className='tile is-ancestor'>
            <div className='tile is-6 is-vertical is-parent'>
              <div className='tile is-child box'>
                <p className='subtitle'>Coverage summaries</p>
                <img src='screenshots/filelist.png' />
              </div>
            </div>
            <div className='tile is-6 is-vertical is-parent'>
              <div className='tile is-child box'>
                <p className='subtitle'>File coverage</p>
                <img src='screenshots/coverage.png' />
              </div>
            </div>
          </div>
        </section>
        <div className='section'>
          <div class='columns'>
            <div class='column'>
              <a href='/docs/integration' className='box'>
                <h2 className='title'>Integration</h2>
                Integrating with your open source project
              </a>
            </div>
            <div class='column'>
              <a href='/docs/hosting' className='box'>
                <h2 className='title'>Hosting</h2>
                Host private projects yourself
              </a>
            </div>
            <div class='column'>
              <a
                href='https://github.com/vangheem/opencoverage'
                className='box'
              >
                <h2 className='title'>Contribute</h2>
                Help make Open Coverage better
              </a>
            </div>
          </div>
        </div>
      </div>

      <div className='container'>
        <RecentPRs />
        <RecentCommits />
      </div>
    </Layout>
  )
}
