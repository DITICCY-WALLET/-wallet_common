import logging
from logging.config import dictConfig

try:
    from config.config import config
    LOG_CONF = config.LOG_CONF
    logger_name = config.logger_name if hasattr(config, 'logger_name') else 'default'
except ImportError:
    LOG_CONF = {'version': 1,
                'disable_existing_loggers': False,
                'formatters':
                    {
                        'standard': {
                            'format': '[%(asctime)s] {%(filename)s %(lineno)d} %(levelname)s - %(message)s'
                            }
                    },
                'handlers': {
                    'console': {
                        'level': 'INFO',
                        'formatter': 'standard',
                        'class': 'logging.StreamHandler',
                        'stream': 'ext://sys.stdout'
                    },
                    'debug': {
                        'level': 'DEBUG',
                        'formatter': 'standard',
                        'class': 'logging.StreamHandler',
                        'stream': 'ext://sys.stdout'
                        },
                    'file': {
                        'class': 'logging.handlers.TimedRotatingFileHandler',
                        'level': 'INFO',
                        'formatter': 'standard',
                        'filename': '/var/logs/apps/default.log',
                        'when': 'D',
                        'interval': 1
                    }
                    },
                'loggers': {
                    'default': {
                        'handlers': ['console', 'file'],
                        'level': 'INFO',
                        'propagate': False
                        },
                    'debug': {
                        'handlers': ['debug'],
                        'level': 'DEBUG',
                        'propagate': False
                        }
                    }
                }

    logger_name = 'default'

dictConfig(LOG_CONF)
logger = logging.getLogger(logger_name)


def logger_attr(cls):
    if not hasattr(cls, 'logger'):
        setattr(cls, 'logger', logger)
    return cls


if __name__ == '__main__':
    dictConfig(LOG_CONF)
    logger = logging.getLogger('default')
    x = 'hello'
    logger.error(x)
    logger.warning(x)
    logger.info(x)
    logger.debug(x)
