package Package1;

import java.io.ByteArrayOutputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.io.PrintStream;
import java.util.Hashtable;
import java.util.Properties;

import javax.ejb.EJBException;
import javax.ejb.MessageDrivenBean;
import javax.ejb.MessageDrivenContext;
import javax.jms.JMSException;
import javax.jms.Message;
import javax.jms.MessageListener;
import javax.jms.Queue;
import javax.jms.QueueConnection;
import javax.jms.QueueConnectionFactory;
import javax.jms.QueueSender;
import javax.jms.QueueSession;
import javax.jms.Session;
import javax.jms.TextMessage;
import javax.naming.Context;
import javax.naming.InitialContext;
import javax.naming.NamingException;

import org.apache.log4j.Logger;
import org.apache.log4j.xml.DOMConfigurator;

import com.att.sam.common.log.LogManager;

/**
* @author ncheppal
* 
 *         This MDB is used to pick the messages from Foreign(Tibco) JMS server,
*         and then place the messages into the Local JMS Server. These Local
*         messages can be processed later using another MDB. The configurations
*         are read from properties file "atlas2SAMProperties".
*/

public class AtlasEventListenerMDB implements MessageDrivenBean,
        MessageListener
{

    private static final long      serialVersionUID    = 1L;
    private static Logger          LOG                 = LogManager.getLogger( "push.atlas.message.to.sam.queue" );
    private static Properties      atlas2SAMProperties = null;
    private MessageDrivenContext   m_context;
    private QueueConnectionFactory qconFactory;
    private QueueConnection        qcon;
    private QueueSession           qsession;
    private QueueSender            qsender;
    private Queue                  queue;

    static
    {
        atlas2SAMProperties = new Properties();
        InputStream inputFile;
        try
        {
            inputFile = Thread.currentThread().getContextClassLoader().getResource( "atlas2sam.properties" ).openStream();
            atlas2SAMProperties.load( inputFile );
        }
        catch ( FileNotFoundException e )
        {
            LOG.error( "@ERROR: " + "Failed to load properties:"
                       + e.getMessage() );
            LOG.error( StackTraceToString( e ) );
        }
        catch ( IOException e )
        {
            LOG.error( "@ERROR: " + "Failed to load properties:"
                       + e.getMessage() );
            LOG.error( StackTraceToString( e ) );
        }

    }

    /**
     * Sets the session context.
     * 
     * @param ctx MessageDrivenContext Context for session
     */
    public void setMessageDrivenContext( MessageDrivenContext ctx )
    {
        m_context = ctx;
    }

    private final String        JNDI_FACTORY     = atlas2SAMProperties.getProperty( Context.URL_PKG_PREFIXES );
    private final String        PROVIDER_URL     = atlas2SAMProperties.getProperty( Context.PROVIDER_URL );

    // Defines the JMS context factory.
    private final String        JMS_FACTORY      = atlas2SAMProperties.getProperty( "jms.queue.connection.factory" );
    private final String        USE_PROVIDER_URL = atlas2SAMProperties.getProperty( "sam.atlas.use.provider.url" );

    // Defines the queue.
    private final static String QUEUE            = atlas2SAMProperties.getProperty( "jms.queue.name" );

    public void onMessage( Message msg )
    {
        try
        {
            LOG.info( "*********** Atlas Event Received *********** " );
            LOG.info( ((TextMessage) msg).getText() );
            msg.setJMSExpiration( Message.DEFAULT_TIME_TO_LIVE );
            InitialContext ic = getInitialContext( PROVIDER_URL );
            init( ic,
                  QUEUE );
            LOG.info( "Initialization done, send message" );
            qsender.send( msg );
            LOG.info( "************Message sent to Local-Queue successfully.***********" );
            close();
        }
        catch ( Exception ex )
        {
            LOG.error( "@ERROR: " + "Failed to process:" + ex.getMessage() );
            LOG.error( StackTraceToString( ex ) );
        }
    }

    public void init( Context ctx,
                      String queueName )
                                        throws NamingException, JMSException
    {
        qconFactory = (QueueConnectionFactory) ctx.lookup( JMS_FACTORY );
        qcon = qconFactory.createQueueConnection();
        qsession = qcon.createQueueSession( false,
                                            Session.AUTO_ACKNOWLEDGE );
        queue = (Queue) ctx.lookup( queueName );
        qsender = qsession.createSender( queue );
        qcon.start();
    }

    public void close()
                       throws JMSException
    {
        qsender.close();
        qsession.close();
        qcon.close();
    }

    private InitialContext getInitialContext( String url )
                                                          throws NamingException
    {
        // As per BEA recommendations, URL is not required. Defect#166029
        InitialContext context = null;
        if ( USE_PROVIDER_URL != null
             && USE_PROVIDER_URL.trim().equalsIgnoreCase( "TRUE" ) )
        {
            Hashtable<String, String> env = new Hashtable<String, String>();
            env.put( Context.INITIAL_CONTEXT_FACTORY,
                     JNDI_FACTORY );
            env.put( Context.PROVIDER_URL,
                     url );
            context = new InitialContext( env );
        }
        else
            context = new InitialContext();

        return context;
    }

    private static String StackTraceToString( Exception e )
    {
        ByteArrayOutputStream b = new ByteArrayOutputStream();
        PrintStream p = new PrintStream( b );
        e.printStackTrace( p );
        p.flush();
        return b.toString();
   }

    public void ejbRemove()
                           throws EJBException
    {
        // TODO Auto-generated method stub

    }

}
