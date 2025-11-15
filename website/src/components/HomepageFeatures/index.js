import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

const FeatureList = [
  {
    title: '🚀 Sync & Async API',
    description: (
      <>
        Choose between synchronous and asynchronous API styles to match your needs.
      </>
    ),
  },
  {
    title: '🔒 Security',
    description: (
      <>
        Built-in authentication and token handling for secure API access.
      </>
    ),
  },
  {
    title: '⚡ Type Hints',
    description: (
      <>
        Full type hint support for better IDE autocompletion and type safety.
      </>
    ),
  },
];

function Feature({title, description}) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}

